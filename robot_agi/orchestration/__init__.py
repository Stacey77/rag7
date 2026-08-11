"""Agentic orchestration: a central brain coordinating specialized sub-agents.

Provides the message-passing framework (bus + A2A messages), the base Agent,
the Orchestrator that delegates over a shared context, and a KnowledgeRetriever
interface that is the plug-in point for RAG / vector databases.
"""
from .agent import Agent
from .bus import MessageBus
from .knowledge import InMemoryKnowledge, KnowledgeRetriever
from .message import Message
from .orchestrator import Orchestrator

__all__ = [
    "Agent",
    "MessageBus",
    "Message",
    "Orchestrator",
    "KnowledgeRetriever",
    "InMemoryKnowledge",
]
