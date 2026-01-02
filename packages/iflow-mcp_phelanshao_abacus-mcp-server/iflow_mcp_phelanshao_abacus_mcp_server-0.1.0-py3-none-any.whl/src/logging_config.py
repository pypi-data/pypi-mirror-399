# src/logging_config.py
"""
Centralized logging configuration for ABACUS MCP Server.
Provides structured logging with different levels and output formats.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import json

class AbacusLogFormatter(logging.Formatter):
    """Custom formatter for ABACUS MCP Server logs."""
    
    def __init__(self):
        super().__init__()
        self.start_time = datetime.now()
    
    def format(self, record):
        # Create structured log entry
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'task_id'):
            log_entry["task_id"] = record.task_id
        if hasattr(record, 'calculation_type'):
            log_entry["calculation_type"] = record.calculation_type
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        if hasattr(record, 'execution_time'):
            log_entry["execution_time_ms"] = record.execution_time
        if hasattr(record, 'memory_usage'):
            log_entry["memory_usage_mb"] = record.memory_usage
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)

class AbacusLogger:
    """Centralized logger for ABACUS MCP Server."""
    
    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = log_dir
        self.loggers = {}
        self._setup_logging_directory()
        self._setup_loggers()
    
    def _setup_logging_directory(self):
        """Create logging directory if it doesn't exist."""
        os.makedirs(self.log_dir, exist_ok=True)
    
    def _setup_loggers(self):
        """Setup different loggers for different purposes."""
        
        # Main application logger
        self.app_logger = self._create_logger(
            name="abacus_mcp.app",
            filename="app.log",
            level=logging.INFO
        )
        
        # Calculation logger
        self.calc_logger = self._create_logger(
            name="abacus_mcp.calculations",
            filename="calculations.log",
            level=logging.INFO
        )
        
        # Error logger
        self.error_logger = self._create_logger(
            name="abacus_mcp.errors",
            filename="errors.log",
            level=logging.ERROR
        )
        
        # Performance logger
        self.perf_logger = self._create_logger(
            name="abacus_mcp.performance",
            filename="performance.log",
            level=logging.INFO
        )
        
        # Audit logger (for tracking user actions)
        self.audit_logger = self._create_logger(
            name="abacus_mcp.audit",
            filename="audit.log",
            level=logging.INFO
        )
    
    def _create_logger(self, name: str, filename: str, level: int) -> logging.Logger:
        """Create a logger with file and console handlers."""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(self.log_dir, filename),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(AbacusLogFormatter())
        
        # Console handler for development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_app_event(self, message: str, level: str = "info", **kwargs):
        """Log general application events."""
        log_func = getattr(self.app_logger, level.lower(), self.app_logger.info)
        log_func(message, extra=kwargs)
    
    def log_calculation_start(self, task_id: str, calculation_type: str, 
                            input_params: Dict[str, Any], user_id: Optional[str] = None):
        """Log the start of a calculation."""
        self.calc_logger.info(
            f"Calculation started: {calculation_type}",
            extra={
                "task_id": task_id,
                "calculation_type": calculation_type,
                "user_id": user_id,
                "input_params": json.dumps(input_params, default=str)
            }
        )
    
    def log_calculation_end(self, task_id: str, calculation_type: str, 
                          success: bool, execution_time_ms: float,
                          result_summary: Optional[Dict[str, Any]] = None):
        """Log the completion of a calculation."""
        status = "SUCCESS" if success else "FAILED"
        self.calc_logger.info(
            f"Calculation completed: {calculation_type} - {status}",
            extra={
                "task_id": task_id,
                "calculation_type": calculation_type,
                "execution_time": execution_time_ms,
                "success": success,
                "result_summary": json.dumps(result_summary, default=str) if result_summary else None
            }
        )
    
    def log_error(self, message: str, error: Exception, task_id: Optional[str] = None,
                  calculation_type: Optional[str] = None, **kwargs):
        """Log errors with full context."""
        self.error_logger.error(
            message,
            exc_info=True,
            extra={
                "task_id": task_id,
                "calculation_type": calculation_type,
                "error_type": type(error).__name__,
                "error_message": str(error),
                **kwargs
            }
        )
    
    def log_performance(self, operation: str, execution_time_ms: float,
                       memory_usage_mb: Optional[float] = None, **kwargs):
        """Log performance metrics."""
        self.perf_logger.info(
            f"Performance: {operation}",
            extra={
                "operation": operation,
                "execution_time": execution_time_ms,
                "memory_usage": memory_usage_mb,
                **kwargs
            }
        )
    
    def log_user_action(self, action: str, user_id: Optional[str] = None,
                       resource: Optional[str] = None, **kwargs):
        """Log user actions for audit purposes."""
        self.audit_logger.info(
            f"User action: {action}",
            extra={
                "action": action,
                "user_id": user_id,
                "resource": resource,
                "timestamp": datetime.now().isoformat(),
                **kwargs
            }
        )
    
    def log_validation_result(self, validation_type: str, success: bool,
                            issues: list, **kwargs):
        """Log validation results."""
        self.app_logger.info(
            f"Validation {validation_type}: {'PASSED' if success else 'FAILED'}",
            extra={
                "validation_type": validation_type,
                "success": success,
                "issues_count": len(issues),
                "issues": json.dumps(issues, default=str),
                **kwargs
            }
        )
    
    def log_resource_access(self, resource_uri: str, user_id: Optional[str] = None,
                          success: bool = True, **kwargs):
        """Log resource access events."""
        self.audit_logger.info(
            f"Resource access: {resource_uri}",
            extra={
                "resource_uri": resource_uri,
                "user_id": user_id,
                "success": success,
                **kwargs
            }
        )
    
    def log_prompt_usage(self, prompt_name: str, user_id: Optional[str] = None,
                        parameters: Optional[Dict[str, Any]] = None):
        """Log prompt usage for analytics."""
        self.audit_logger.info(
            f"Prompt used: {prompt_name}",
            extra={
                "prompt_name": prompt_name,
                "user_id": user_id,
                "parameters": json.dumps(parameters, default=str) if parameters else None
            }
        )

# Global logger instance
abacus_logger = AbacusLogger()

# Convenience functions for easy access
def log_app_event(message: str, level: str = "info", **kwargs):
    """Log general application events."""
    abacus_logger.log_app_event(message, level, **kwargs)

def log_calculation_start(task_id: str, calculation_type: str, 
                         input_params: Dict[str, Any], user_id: Optional[str] = None):
    """Log the start of a calculation."""
    abacus_logger.log_calculation_start(task_id, calculation_type, input_params, user_id)

def log_calculation_end(task_id: str, calculation_type: str, 
                       success: bool, execution_time_ms: float,
                       result_summary: Optional[Dict[str, Any]] = None):
    """Log the completion of a calculation."""
    abacus_logger.log_calculation_end(task_id, calculation_type, success, execution_time_ms, result_summary)

def log_error(message: str, error: Exception, task_id: Optional[str] = None,
              calculation_type: Optional[str] = None, **kwargs):
    """Log errors with full context."""
    abacus_logger.log_error(message, error, task_id, calculation_type, **kwargs)

def log_performance(operation: str, execution_time_ms: float,
                   memory_usage_mb: Optional[float] = None, **kwargs):
    """Log performance metrics."""
    abacus_logger.log_performance(operation, execution_time_ms, memory_usage_mb, **kwargs)

def log_user_action(action: str, user_id: Optional[str] = None,
                   resource: Optional[str] = None, **kwargs):
    """Log user actions for audit purposes."""
    abacus_logger.log_user_action(action, user_id, resource, **kwargs)

def log_validation_result(validation_type: str, success: bool,
                         issues: list, **kwargs):
    """Log validation results."""
    abacus_logger.log_validation_result(validation_type, success, issues, **kwargs)

def log_resource_access(resource_uri: str, user_id: Optional[str] = None,
                       success: bool = True, **kwargs):
    """Log resource access events."""
    abacus_logger.log_resource_access(resource_uri, user_id, success, **kwargs)

def log_prompt_usage(prompt_name: str, user_id: Optional[str] = None,
                    parameters: Optional[Dict[str, Any]] = None):
    """Log prompt usage for analytics."""
    abacus_logger.log_prompt_usage(prompt_name, user_id, parameters)