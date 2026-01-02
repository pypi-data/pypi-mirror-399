"""Tests for SiloWorker Python SDK."""

import pytest
from unittest.mock import Mock, patch
from siloworker import SiloWorker, ValidationError, AuthenticationError
from siloworker.types import WorkflowNode, WorkflowConnection


class TestSiloWorker:
    """Test SiloWorker client."""
    
    def test_init_with_string_api_key(self):
        """Test initialization with string API key."""
        client = SiloWorker("test-api-key")
        assert client.http.api_key == "test-api-key"
    
    def test_init_with_config_dict(self):
        """Test initialization with config dictionary."""
        config = {
            "api_key": "test-api-key",
            "base_url": "https://custom.api.com",
            "timeout": 60
        }
        client = SiloWorker(config)
        assert client.http.api_key == "test-api-key"
        assert client.http.base_url == "https://custom.api.com"
        assert client.http.timeout == 60
    
    def test_init_without_api_key(self):
        """Test initialization without API key raises error."""
        with pytest.raises(ValidationError):
            SiloWorker("")
    
    @patch('siloworker.http.HttpClient.post')
    def test_create_agent(self, mock_post):
        """Test creating an agent."""
        mock_post.return_value = {"agent_id": "agent_123", "webhook_secret": "secret"}
        
        client = SiloWorker("test-api-key")
        
        nodes = [WorkflowNode(id="node1", type="http", config={})]
        connections = [WorkflowConnection(from_node="node1", to="node2")]
        
        result = client.create_agent(
            project_id="prj_123",
            name="Test Agent",
            nodes=nodes,
            connections=connections
        )
        
        assert result["agent_id"] == "agent_123"
        mock_post.assert_called_once()
    
    @patch('siloworker.http.HttpClient.get')
    def test_list_agents(self, mock_get):
        """Test listing agents."""
        mock_get.return_value = [{"agent_id": "agent_123", "name": "Test Agent"}]
        
        client = SiloWorker("test-api-key")
        result = client.list_agents()
        
        assert len(result) == 1
        assert result[0]["agent_id"] == "agent_123"
        mock_get.assert_called_once_with("/v1/agents")
    
    @patch('siloworker.http.HttpClient.post')
    def test_start_run(self, mock_post):
        """Test starting a run."""
        mock_post.return_value = {"run_id": "run_123", "status": "queued"}
        
        client = SiloWorker("test-api-key")
        result = client.start_run("agent_123", {"email": "test@example.com"})
        
        assert result["run_id"] == "run_123"
        mock_post.assert_called_once()
    
    @patch('siloworker.http.HttpClient.post')
    def test_resume_run(self, mock_post):
        """Test resuming a run."""
        mock_post.return_value = {
            "run_id": "run_456", 
            "message": "Run resumed", 
            "original_run_id": "run_123"
        }
        
        client = SiloWorker("test-api-key")
        result = client.resume_run("run_123", "step_2")
        
        assert result["run_id"] == "run_456"
        mock_post.assert_called_once_with("/v1/runs/run_123/resume", {"from_step": "step_2"})
    
    @patch('siloworker.http.HttpClient.get')
    def test_ping(self, mock_get):
        """Test health check."""
        mock_get.return_value = {"workspace_id": "ws_123"}
        
        client = SiloWorker("test-api-key")
        result = client.ping()
        
        assert result["status"] == "ok"
        assert "timestamp" in result
    
    def test_version(self):
        """Test SDK version."""
        assert SiloWorker.version() == "1.0.0"


class TestWorkflowValidation:
    """Test workflow validation logic."""
    
    def test_workflow_node_creation(self):
        """Test creating workflow nodes."""
        node = WorkflowNode(
            id="test_node",
            type="http",
            config={"url": "https://api.example.com"}
        )
        
        assert node.id == "test_node"
        assert node.type == "http"
        assert node.config["url"] == "https://api.example.com"
    
    def test_workflow_connection_creation(self):
        """Test creating workflow connections."""
        connection = WorkflowConnection(
            from_node="node1",
            to="node2",
            condition="success"
        )
        
        assert connection.from_node == "node1"
        assert connection.to == "node2"
        assert connection.condition == "success"
