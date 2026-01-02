"""Main SiloWorker client."""

import time
from typing import Any, Dict, List, Optional, Union, Iterator

from .http import HttpClient
from .types import (
    Agent, Run, Project, Schedule, Workspace, Template, Tool,
    WorkflowNode, WorkflowConnection, Trigger, RetryPolicy, SiloWorkerConfig
)


class SiloWorker:
    """Main SiloWorker client for workflow automation."""
    
    def __init__(self, config: Union[str, SiloWorkerConfig]) -> None:
        """Initialize SiloWorker client.
        
        Args:
            config: API key string or configuration dictionary
        """
        if isinstance(config, str):
            config = {"api_key": config}
        
        self.http = HttpClient(
            api_key=config["api_key"],
            base_url=config.get("base_url", "https://api.siloworker.dev"),
            timeout=config.get("timeout", 30),
            retries=config.get("retries", 3),
            debug=config.get("debug", False)
        )
    
    # Agent methods
    def create_agent(
        self,
        project_id: str,
        name: str,
        nodes: List[WorkflowNode],
        connections: List[WorkflowConnection],
        description: Optional[str] = None,
        trigger: Optional[Trigger] = None,
        retry_policy: Optional[RetryPolicy] = None,
        timeout_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a new workflow agent."""
        data = {
            "project_id": project_id,
            "name": name,
            "nodes": [node.__dict__ for node in nodes],
            "connections": [{"from": conn.from_node, "to": conn.to, "condition": conn.condition} for conn in connections]
        }
        
        if description:
            data["description"] = description
        if trigger:
            data["trigger"] = trigger.__dict__
        if retry_policy:
            data["retry_policy"] = retry_policy.__dict__
        if timeout_seconds:
            data["timeout_seconds"] = timeout_seconds
            
        return self.http.post("/v1/agents", data)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents in workspace."""
        return self.http.get("/v1/agents")
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get agent by ID."""
        return self.http.get(f"/v1/agents/{agent_id}")
    
    def update_agent(
        self,
        agent_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        nodes: Optional[List[WorkflowNode]] = None,
        connections: Optional[List[WorkflowConnection]] = None,
        trigger: Optional[Trigger] = None,
        retry_policy: Optional[RetryPolicy] = None,
        timeout_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """Update an existing agent."""
        data = {}
        
        if name:
            data["name"] = name
        if description:
            data["description"] = description
        if nodes:
            data["nodes"] = [node.__dict__ for node in nodes]
        if connections:
            data["connections"] = [{"from": conn.from_node, "to": conn.to, "condition": conn.condition} for conn in connections]
        if trigger:
            data["trigger"] = trigger.__dict__
        if retry_policy:
            data["retry_policy"] = retry_policy.__dict__
        if timeout_seconds:
            data["timeout_seconds"] = timeout_seconds
            
        return self.http.put(f"/v1/agents/{agent_id}", data)
    
    def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        """Delete an agent."""
        return self.http.delete(f"/v1/agents/{agent_id}")
    
    # Run methods
    def start_run(
        self,
        agent_id: str,
        input_data: Optional[Dict[str, Any]] = None,
        webhook: Optional[str] = None,
        trigger_type: str = "manual",
        run_async: bool = True
    ) -> Dict[str, Any]:
        """Start a new workflow run."""
        data = {
            "agent_id": agent_id,
            "input": input_data or {},
            "trigger_type": trigger_type,
            "run_async": run_async
        }
        
        if webhook:
            data["webhook"] = webhook
            
        return self.http.post("/v1/runs", data)
    
    def get_run(self, run_id: str) -> Dict[str, Any]:
        """Get run by ID."""
        return self.http.get(f"/v1/runs/{run_id}")
    
    def list_runs(
        self,
        limit: Optional[int] = None,
        status: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List runs in workspace."""
        params = []
        if limit:
            params.append(f"limit={limit}")
        if status:
            params.append(f"status={status}")
        if agent_id:
            params.append(f"agent_id={agent_id}")
        
        query = "?" + "&".join(params) if params else ""
        return self.http.get(f"/v1/runs{query}")
    
    def resume_run(self, run_id: str, from_step: Optional[str] = None) -> Dict[str, Any]:
        """Resume a failed run."""
        data = {}
        if from_step:
            data["from_step"] = from_step
        return self.http.post(f"/v1/runs/{run_id}/resume", data)
    
    def cancel_run(self, run_id: str) -> Dict[str, Any]:
        """Cancel a running run."""
        return self.http.post(f"/v1/runs/{run_id}/cancel")
    
    def wait_for_completion(
        self,
        run_id: str,
        timeout: int = 300,
        poll_interval: int = 2,
        on_progress: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Wait for run completion with polling."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            run = self.get_run(run_id)
            
            if on_progress:
                on_progress(run)
            
            if run["status"] in ["completed", "failed", "cancelled"]:
                return run
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Run {run_id} did not complete within {timeout} seconds")
    
    def stream_progress(self, run_id: str) -> Iterator[Dict[str, Any]]:
        """Stream run progress with polling."""
        last_status = ""
        
        while True:
            run = self.get_run(run_id)
            
            if run["status"] != last_status:
                last_status = run["status"]
                yield run
            
            if run["status"] in ["completed", "failed", "cancelled"]:
                break
            
            time.sleep(1)
    
    # Project methods
    def create_project(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new project."""
        data = {"name": name}
        if description:
            data["description"] = description
        return self.http.post("/v1/projects", data)
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects."""
        return self.http.get("/v1/projects")
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get project by ID."""
        return self.http.get(f"/v1/projects/{project_id}")
    
    def update_project(
        self,
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a project."""
        data = {}
        if name:
            data["name"] = name
        if description:
            data["description"] = description
        return self.http.put(f"/v1/projects/{project_id}", data)
    
    def delete_project(self, project_id: str) -> Dict[str, Any]:
        """Delete a project."""
        return self.http.delete(f"/v1/projects/{project_id}")
    
    # Schedule methods
    def create_schedule(
        self,
        agent_id: str,
        input_data: Optional[Dict[str, Any]] = None,
        cron: Optional[str] = None,
        interval_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a new schedule."""
        data = {
            "agent_id": agent_id,
            "input": input_data or {}
        }
        
        if cron:
            data["cron"] = cron
        if interval_seconds:
            data["interval_seconds"] = interval_seconds
            
        return self.http.post("/v1/schedules", data)
    
    def list_schedules(self) -> Dict[str, Any]:
        """List all schedules."""
        return self.http.get("/v1/schedules")
    
    def get_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """Get schedule by ID."""
        return self.http.get(f"/v1/schedules/{schedule_id}")
    
    def update_schedule(
        self,
        schedule_id: str,
        input_data: Optional[Dict[str, Any]] = None,
        cron: Optional[str] = None,
        interval_seconds: Optional[int] = None,
        enabled: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Update a schedule."""
        data = {}
        if input_data:
            data["input"] = input_data
        if cron:
            data["cron"] = cron
        if interval_seconds:
            data["interval_seconds"] = interval_seconds
        if enabled is not None:
            data["enabled"] = enabled
            
        return self.http.put(f"/v1/schedules/{schedule_id}", data)
    
    def delete_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """Delete a schedule."""
        return self.http.delete(f"/v1/schedules/{schedule_id}")
    
    def enable_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """Enable a schedule."""
        return self.update_schedule(schedule_id, enabled=True)
    
    def disable_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """Disable a schedule."""
        return self.update_schedule(schedule_id, enabled=False)
    
    # Workspace methods
    def get_workspace(self) -> Dict[str, Any]:
        """Get workspace information."""
        return self.http.get("/v1/workspace")
    
    def update_workspace_settings(self, api_keys: Dict[str, Any]) -> Dict[str, Any]:
        """Update workspace API keys."""
        return self.http.put("/v1/workspace/settings", {"api_keys": api_keys})
    
    def regenerate_api_key(self) -> Dict[str, Any]:
        """Regenerate workspace API key."""
        return self.http.post("/v1/workspace/regenerate-key")
    
    # Template methods
    def list_templates(self) -> List[Dict[str, Any]]:
        """List available templates."""
        return self.http.get("/v1/templates")
    
    def get_template(self, template_id: str) -> Dict[str, Any]:
        """Get template by ID."""
        return self.http.get(f"/v1/templates/{template_id}")
    
    # Tools methods
    def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        return self.http.get("/v1/tools")
    
    def list_triggers(self) -> Dict[str, Any]:
        """List available triggers."""
        return self.http.get("/v1/triggers")
    
    # Convenience methods
    def execute_workflow(
        self,
        agent_id: str,
        input_data: Optional[Dict[str, Any]] = None,
        wait: bool = False,
        timeout: int = 300,
        on_progress: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Execute workflow with optional waiting."""
        result = self.start_run(agent_id, input_data)
        
        if wait:
            return self.wait_for_completion(
                result["run_id"],
                timeout=timeout,
                on_progress=on_progress
            )
        
        return result
    
    def bulk_resume_failed(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Resume all failed runs."""
        data = {"status_filter": "failed"}
        if agent_id:
            data["agent_id"] = agent_id
        return self.http.post("/v1/runs/bulk-resume", data)
    
    def ping(self) -> Dict[str, Any]:
        """Health check."""
        try:
            self.get_workspace()
            return {
                "status": "ok",
                "timestamp": time.time()
            }
        except Exception as e:
            raise Exception(f"SiloWorker API health check failed: {e}")
    
    @staticmethod
    def version() -> str:
        """Get SDK version."""
        return "1.0.0"
