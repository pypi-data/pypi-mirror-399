"""
Tests for SystemPromptManager class.
"""

import pytest
from swarms_spm import SystemPromptManager


class TestSystemPromptManager:
    """Test suite for SystemPromptManager."""

    def test_set_and_get_global_prompt(self):
        """Test setting and getting global system prompt."""
        SystemPromptManager.set_global_system_prompt("Test global prompt")
        assert SystemPromptManager.get_global_system_prompt() == "Test global prompt"
        SystemPromptManager.clear_global_system_prompt()

    def test_clear_global_prompt(self):
        """Test clearing global system prompt."""
        SystemPromptManager.set_global_system_prompt("Test prompt")
        SystemPromptManager.clear_global_system_prompt()
        assert SystemPromptManager.get_global_system_prompt() is None

    def test_instance_uses_class_global_prompt(self):
        """Test that instance uses class-level global prompt when not overridden."""
        SystemPromptManager.set_global_system_prompt("Class global prompt")
        manager = SystemPromptManager()
        result = manager.assemble_system_prompts(system_prompt="Main prompt")
        assert "[Global System Prompt]" in result
        assert "Class global prompt" in result
        SystemPromptManager.clear_global_system_prompt()

    def test_instance_override_global_prompt(self):
        """Test that instance can override class-level global prompt."""
        SystemPromptManager.set_global_system_prompt("Class global")
        manager = SystemPromptManager(global_system_prompt="Instance global")
        result = manager.assemble_system_prompts(system_prompt="Main prompt")
        assert "Instance global" in result
        assert "Class global" not in result
        SystemPromptManager.clear_global_system_prompt()

    def test_assemble_with_secondary_prompt(self):
        """Test assembling prompts with secondary system prompt."""
        manager = SystemPromptManager(secondary_system_prompt="Secondary prompt")
        result = manager.assemble_system_prompts(system_prompt="Main prompt")
        assert "[System Prompt]" in result
        assert "Main prompt" in result
        assert "[Secondary System Prompt]" in result
        assert "Secondary prompt" in result

    def test_assemble_with_numbered_prompts(self):
        """Test assembling prompts with numbered prompts."""
        manager = SystemPromptManager()
        result = manager.assemble_system_prompts(
            system_prompt="Main prompt",
            system_prompts_n={2: "Prompt 2", 3: "Prompt 3", 1: "Prompt 1"}
        )
        assert "[System Prompt 1]" in result
        assert "[System Prompt 2]" in result
        assert "[System Prompt 3]" in result
        # Check ordering (should be sorted)
        idx_1 = result.find("[System Prompt 1]")
        idx_2 = result.find("[System Prompt 2]")
        idx_3 = result.find("[System Prompt 3]")
        assert idx_1 < idx_2 < idx_3

    def test_assemble_empty_prompts(self):
        """Test assembling with no prompts returns empty string."""
        manager = SystemPromptManager()
        result = manager.assemble_system_prompts()
        assert result == ""

    def test_hierarchical_order(self):
        """Test that prompts are assembled in correct hierarchical order."""
        SystemPromptManager.set_global_system_prompt("Global")
        manager = SystemPromptManager(secondary_system_prompt="Secondary")
        result = manager.assemble_system_prompts(
            system_prompt="Main",
            system_prompts_n={2: "Numbered 2"}
        )
        
        # Check order: Global -> Main -> Secondary -> Numbered
        idx_global = result.find("[Global System Prompt]")
        idx_main = result.find("[System Prompt]")
        idx_secondary = result.find("[Secondary System Prompt]")
        idx_numbered = result.find("[System Prompt 2]")
        
        assert idx_global < idx_main < idx_secondary < idx_numbered
        SystemPromptManager.clear_global_system_prompt()

    def test_multiple_instances_share_global(self):
        """Test that multiple instances share the same class-level global prompt."""
        SystemPromptManager.set_global_system_prompt("Shared global")
        manager1 = SystemPromptManager()
        manager2 = SystemPromptManager()
        
        result1 = manager1.assemble_system_prompts(system_prompt="Prompt 1")
        result2 = manager2.assemble_system_prompts(system_prompt="Prompt 2")
        
        assert "Shared global" in result1
        assert "Shared global" in result2
        SystemPromptManager.clear_global_system_prompt()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

