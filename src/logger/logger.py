import logging
import json
import time
import functools
from datetime import datetime
from pathlib import Path

class JsonFormatter(logging.Formatter):
    """
    Formats log records as a JSON string.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        
        if hasattr(record, "run_id"):
            log_record["run_id"] = record.run_id
        if hasattr(record, "duration_ms"):
            log_record["duration_ms"] = record.duration_ms
        if hasattr(record, "node_name"):
            log_record["node_name"] = record.node_name

        return json.dumps(log_record)

LOG_START_TS = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"agent_langgraph-{LOG_START_TS}.log"

def setup_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.FileHandler(LOG_FILE)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.propagate = False

    return logger

def monitor_node(func):
    """
    Decorator to log node entry, exit, and execution time with Run ID.
    Assumes the first argument to the function is 'state' (AgentState).
    """
    logger = setup_logger("orchestrator")

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        state = args[0] if args else {}
        run_id = state.get("run_id", "unknown-run")
        node_name = func.__name__

        start_time = time.time()
        
        logger.info(
            f"Starting Node: {node_name}", 
            extra={"run_id": run_id, "node_name": node_name, "event": "node_start"}
        )

        try:
            result = func(*args, **kwargs)
            
            duration = (time.time() - start_time) * 1000 # ms
            logger.info(
                f"Finished Node: {node_name}", 
                extra={
                    "run_id": run_id, 
                    "node_name": node_name, 
                    "duration_ms": round(duration, 2),
                    "event": "node_complete"
                }
            )
            return result
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(
                f"Node Failed: {node_name} - {str(e)}", 
                extra={
                    "run_id": run_id, 
                    "node_name": node_name, 
                    "duration_ms": round(duration, 2),
                    "event": "node_error"
                }
            )
            raise e

    return wrapper