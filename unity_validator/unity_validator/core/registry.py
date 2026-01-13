# SPDX-License-Identifier: GPL-3.0-or-later
"""
Checker registry for managing validation checkers.
"""

from typing import Dict, List, Type, Optional
import logging

from .base_checker import BaseChecker

logger = logging.getLogger(__name__)


class CheckerRegistry:
    """
    Central registry for all validation checkers.
    
    Provides methods to register, retrieve, and manage checkers.
    Uses class methods to act as a singleton.
    """
    
    _checkers: Dict[str, BaseChecker] = {}
    _checker_classes: Dict[str, Type[BaseChecker]] = {}
    
    @classmethod
    def register(cls, checker_class: Type[BaseChecker]) -> Type[BaseChecker]:
        """
        Register a checker class.
        
        Args:
            checker_class: The checker class to register
            
        Returns:
            The registered class (for decorator usage)
        """
        # Instantiate to validate and get ID
        instance = checker_class()
        checker_id = instance.get_id()
        
        if checker_id in cls._checkers:
            logger.warning(f"Checker '{checker_id}' already registered, overwriting")
        
        cls._checkers[checker_id] = instance
        cls._checker_classes[checker_id] = checker_class
        
        logger.debug(f"Registered checker: {checker_id} ({checker_class.__name__})")
        return checker_class
    
    @classmethod
    def unregister(cls, checker_id: str) -> bool:
        """
        Unregister a checker by ID.
        
        Args:
            checker_id: The ID of the checker to remove
            
        Returns:
            True if removed, False if not found
        """
        if checker_id in cls._checkers:
            del cls._checkers[checker_id]
            del cls._checker_classes[checker_id]
            return True
        return False
    
    @classmethod
    def get(cls, checker_id: str) -> Optional[BaseChecker]:
        """Get a checker instance by ID."""
        return cls._checkers.get(checker_id)
    
    @classmethod
    def get_all(cls) -> List[BaseChecker]:
        """Get all registered checker instances."""
        return list(cls._checkers.values())
    
    @classmethod
    def get_ids(cls) -> List[str]:
        """Get all registered checker IDs."""
        return list(cls._checkers.keys())
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered checkers."""
        cls._checkers.clear()
        cls._checker_classes.clear()
    
    @classmethod
    def count(cls) -> int:
        """Get the number of registered checkers."""
        return len(cls._checkers)


def register_checker(cls: Type[BaseChecker]) -> Type[BaseChecker]:
    """
    Decorator to register a checker class.
    
    Usage:
        @register_checker
        class MyChecker(BaseChecker):
            ...
    """
    return CheckerRegistry.register(cls)
