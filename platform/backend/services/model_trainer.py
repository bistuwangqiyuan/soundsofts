"""Service wrapping ML model training, dispatching to background tasks."""

import asyncio
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from api.schemas.training import ExperimentInfo, ModelMetrics, TrainingStatus
from core.config import get_settings

settings = get_settings()


class ModelTrainerService:
    """Wrap ML model training and dispatch to background tasks (Redis/Celery)."""

    def __init__(self) -> None:
        self._redis_url = settings.redis_url
        self._mlflow_uri = settings.mlflow_tracking_uri

    async def train_model(
        self,
        model_type: str,
        data_path: str,
        config: Optional[Dict[str, Any]] = None,
        run_optimization: bool = False,
    ) -> TrainingStatus:
        """
        Start a training job and dispatch to background task.

        Returns TrainingStatus with job_id and initial status.
        """
        payload = {
            "model_type": model_type,
            "data_path": data_path,
            "config": config or {},
            "run_optimization": run_optimization,
        }
        job_id = self._make_job_id(payload)
        await self._enqueue_training(job_id, payload, run_optimization)
        return TrainingStatus(
            job_id=job_id,
            status="pending",
            progress=0.0,
            metrics=ModelMetrics(),
            message="Training job queued. Poll /training/status/{job_id} for progress.",
            started_at=datetime.now(timezone.utc).isoformat(),
        )

    async def get_training_status(self, job_id: str) -> Optional[TrainingStatus]:
        """Get current training job status from Redis/MLflow."""
        return await asyncio.to_thread(
            self._get_training_status_sync,
            job_id,
        )

    def _get_training_status_sync(self, job_id: str) -> Optional[TrainingStatus]:
        try:
            import redis

            r = redis.from_url(self._redis_url)
            key = f"training:status:{job_id}"
            data = r.get(key)
            if data:
                d = json.loads(data)
                return TrainingStatus(
                    job_id=d.get("job_id", job_id),
                    status=d.get("status", "unknown"),
                    progress=d.get("progress", 0.0),
                    metrics=ModelMetrics(**d.get("metrics", {})),
                    message=d.get("message"),
                    started_at=d.get("started_at"),
                    completed_at=d.get("completed_at"),
                )
        except Exception:
            pass
        return TrainingStatus(
            job_id=job_id,
            status="unknown",
            progress=0.0,
            metrics=ModelMetrics(),
            message="Job not found or Redis unavailable.",
        )

    async def list_experiments(self) -> List[ExperimentInfo]:
        """List MLflow experiments."""
        return await asyncio.to_thread(self._list_experiments_sync)

    def _list_experiments_sync(self) -> List[ExperimentInfo]:
        try:
            import mlflow

            mlflow.set_tracking_uri(self._mlflow_uri)
            experiments = mlflow.search_experiments()
            result: List[ExperimentInfo] = []
            for exp in experiments:
                runs = mlflow.search_runs(
                    experiment_ids=[exp.experiment_id],
                    max_results=10,
                )
                best_run_id = None
                best_metrics: Dict[str, float] = {}
                run_count = len(runs) if runs is not None and not runs.empty else 0
                if runs is not None and not runs.empty:
                    best_run_id = str(runs.iloc[0].get("run_id", ""))
                    for col in runs.columns:
                        if col.startswith("metrics."):
                            v = runs.iloc[0][col]
                            if isinstance(v, (int, float)):
                                best_metrics[col.replace("metrics.", "")] = float(v)
                result.append(
                    ExperimentInfo(
                        experiment_id=exp.experiment_id,
                        name=exp.name or "default",
                        run_count=run_count,
                        best_run_id=best_run_id,
                        best_metrics=best_metrics,
                    )
                )
            return result
        except Exception:
            return [
                ExperimentInfo(
                    experiment_id="0",
                    name="default",
                    run_count=0,
                    best_run_id=None,
                    best_metrics={},
                )
            ]

    def _make_job_id(self, payload: Dict[str, Any]) -> str:
        s = json.dumps(payload, sort_keys=True)
        h = hashlib.sha256(s.encode()).hexdigest()[:12]
        return f"train_{payload.get('model_type', 'unknown')}_{h}"

    async def _enqueue_training(
        self,
        job_id: str,
        payload: Dict[str, Any],
        run_optimization: bool,
    ) -> None:
        """Enqueue training task to Redis for background worker."""
        task_name = "run_optimization_job" if run_optimization else "run_training_job"
        await asyncio.to_thread(
            self._enqueue_training_sync,
            job_id,
            payload,
            task_name,
        )

    def _enqueue_training_sync(
        self,
        job_id: str,
        payload: Dict[str, Any],
        task_name: str,
    ) -> None:
        """Sync enqueue to Redis and store initial pending status."""
        try:
            import redis

            r = redis.from_url(self._redis_url)
            queue_key = "training:queue"
            r.rpush(queue_key, json.dumps({"job_id": job_id, "payload": payload, "task": task_name}))
            status_key = f"training:status:{job_id}"
            r.setex(
                status_key,
                86400,
                json.dumps({
                    "job_id": job_id,
                    "status": "pending",
                    "progress": 0.0,
                    "metrics": {},
                    "message": "Job queued",
                    "started_at": datetime.now(timezone.utc).isoformat(),
                }),
            )
        except Exception:
            pass
