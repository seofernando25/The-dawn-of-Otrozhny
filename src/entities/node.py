import random
from .base import Entity


class Node(Entity):
    """A node in the pathfinding network for enemy patrol routes."""

    def __init__(self, start_pos, *, context=None):
        super().__init__(start_pos, context=context)
        self.behaviour = None
        self.destination_point = 0
        self.nodes = []

    def join_node(self, nextNode):
        """Join this node to another node (bidirectional connection)."""
        if nextNode not in self.nodes:
            self.nodes.append(nextNode)
        if self not in nextNode.nodes:
            nextNode.nodes.append(self)

    def remove_node(self, node):
        """Remove a connection to another node (bidirectional)."""
        if node in self.nodes:
            self.nodes.remove(node)
            node.remove_node(self)

    def pick_random_node(self, biased=False):
        """Pick a random connected node."""
        node_list = self.nodes.copy()

        if biased:
            from config import ENEMY_CONFIG

            bias_factor = ENEMY_CONFIG["node_bias_factor"]
            for _ in range(int(len(self.nodes) * bias_factor)):
                node_list.append(node_list[-1])

        if len(node_list) > 0:
            node_pos = random.randint(0, len(node_list) - 1)
            return node_list[node_pos]
        else:
            return self
