"""
Standalone System Prompt Manager Library

A utility class for managing hierarchical system prompts including global,
primary, secondary, and numbered system prompts. This library has zero
dependencies on the local codebase and can be imported independently.

Usage:
    from swarms_spm import SystemPromptManager
    
    # Set class-level global prompt
    SystemPromptManager.set_global_system_prompt("Global instructions")
    
    # Create instance with optional overrides
    manager = SystemPromptManager(
        global_system_prompt="Instance override",
        secondary_system_prompt="Secondary instructions",
        system_prompts_n={2: "Prompt 2", 3: "Prompt 3"}
    )
    
    # Assemble prompts (uses instance's system_prompts_n)
    combined = manager.assemble_system_prompts(
        system_prompt="Main prompt"
    )
    
    # Or override system_prompts_n in the call
    combined = manager.assemble_system_prompts(
        system_prompt="Main prompt",
        system_prompts_n={4: "Override prompt"}
    )
"""

__version__ = "1.0.1"

from typing import Dict, Optional

__all__ = ["SystemPromptManager", "__version__"]


class SystemPromptManager:
    """
    Manages hierarchical system prompts with support for global, primary,
    secondary, and numbered prompts.
    
    Features:
    - Class-level global system prompt (shared across all instances)
    - Instance-level global system prompt (overrides class-level)
    - Secondary system prompt
    - Numbered system prompts (system_prompt_2, system_prompt_3, etc.)
    - Automatic hierarchical assembly with formatted headers
    """
    
    # Class-level global system prompt that applies to all instances
    _global_system_prompt: Optional[str] = None
    
    def __init__(
        self,
        global_system_prompt: Optional[str] = None,
        secondary_system_prompt: Optional[str] = None,
        system_prompts_n: Optional[Dict[int, str]] = None,
    ):
        """
        Initialize SystemPromptManager instance.

        Args:
            global_system_prompt (Optional[str]): Instance-level global system prompt.
                If provided, overrides the class-level global system prompt.
                If None, falls back to class-level global system prompt.
            secondary_system_prompt (Optional[str]): Secondary system prompt to be
                included in the assembled output.
            system_prompts_n (Optional[Dict[int, str]]): Dictionary of numbered prompts
                where keys are integers (n) and values are prompt strings.
                Example: {2: "Prompt 2", 3: "Prompt 3"}. Defaults to None.
        """
        # Use instance-level global_system_prompt if provided, otherwise fall back to class-level
        self.global_system_prompt = (
            global_system_prompt 
            if global_system_prompt is not None 
            else SystemPromptManager._global_system_prompt
        )
        self.secondary_system_prompt = secondary_system_prompt
        self.system_prompts_n = system_prompts_n or {}
    
    @classmethod
    def set_global_system_prompt(cls, prompt: str) -> None:
        """
        Set a global system prompt that will automatically apply to all instances.

        This allows you to define a system prompt once at the class level, and it will
        be automatically included in all instances without needing to pass it to each instance.

        Args:
            prompt (str): The global system prompt to apply to all instances.

        Examples:
            >>> SystemPromptManager.set_global_system_prompt("You are a helpful AI assistant.")
            >>> manager1 = SystemPromptManager()
            >>> manager2 = SystemPromptManager()
            >>> # Both managers will automatically include the global system prompt
        """
        cls._global_system_prompt = prompt
    
    @classmethod
    def get_global_system_prompt(cls) -> Optional[str]:
        """
        Get the current global system prompt.

        Returns:
            Optional[str]: The current global system prompt, or None if not set.
        """
        return cls._global_system_prompt
    
    @classmethod
    def clear_global_system_prompt(cls) -> None:
        """
        Clear the global system prompt so it no longer applies to new instances.
        """
        cls._global_system_prompt = None
    
    def assemble_system_prompts(
        self,
        system_prompt: Optional[str] = None,
        system_prompts_n: Optional[Dict[int, str]] = None,
    ) -> str:
        """
        Assembles system prompts in hierarchical order with numbered headers.

        Combines prompts in the following order:
        1. Global System Prompt (if provided - checks instance-level first, then class-level)
        2. System Prompt (if provided)
        3. Secondary System Prompt (if provided)
        4. System Prompt N (if provided, sorted by n value)

        Each prompt section is prefixed with a header like [Global System Prompt],
        [System Prompt], [Secondary System Prompt], [System Prompt 2], etc.

        Args:
            system_prompt (Optional[str]): The primary system prompt to include. Defaults to None.
            system_prompts_n (Optional[Dict[int, str]]): Dictionary of numbered prompts
                where keys are integers (n) and values are prompt strings.
                Example: {2: "Prompt 2", 3: "Prompt 3"}. Defaults to None.
                If None, uses the instance's system_prompts_n attribute if set.

        Returns:
            str: Combined system prompt string with headers and separators.
                Returns empty string if no prompts are provided.

        Examples:
            >>> manager = SystemPromptManager(
            ...     secondary_system_prompt="Secondary",
            ...     system_prompts_n={2: "Prompt 2", 3: "Prompt 3"}
            ... )
            >>> result = manager.assemble_system_prompts(system_prompt="Main prompt")
            >>> # Returns formatted string with all prompts combined
            >>> # Can also override system_prompts_n in the call:
            >>> result = manager.assemble_system_prompts(
            ...     system_prompt="Main prompt",
            ...     system_prompts_n={4: "Override prompt"}
            ... )
        """
        prompt_sections = []

        # 1. Global System Prompt (highest priority)
        # Check instance-level first, then fall back to class-level
        global_prompt = (
            self.global_system_prompt
            if self.global_system_prompt is not None
            else SystemPromptManager._global_system_prompt
        )
        if global_prompt is not None:
            prompt_sections.append(
                f"[Global System Prompt]\n{global_prompt}"
            )

        # 2. System Prompt
        if system_prompt is not None:
            prompt_sections.append(
                f"[System Prompt]\n{system_prompt}"
            )

        # 3. Secondary System Prompt
        if self.secondary_system_prompt is not None:
            prompt_sections.append(
                f"[Secondary System Prompt]\n{self.secondary_system_prompt}"
            )

        # 4. System Prompt N (sorted by n value)
        # Use provided system_prompts_n if given, otherwise use instance attribute
        prompts_n = system_prompts_n if system_prompts_n is not None else self.system_prompts_n
        if prompts_n:
            sorted_n = sorted(prompts_n.keys())
            for n in sorted_n:
                prompt_sections.append(
                    f"[System Prompt {n}]\n{prompts_n[n]}"
                )

        # Combine all sections with double newline separator
        return "\n\n".join(prompt_sections)
