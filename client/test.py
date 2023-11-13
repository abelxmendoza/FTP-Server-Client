class Node:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def isBalanced(root):
    def helper(node):
        if node is None:
            return True, 0

        leftBalance, leftHeight = helper(node.left)
        rightBalance, rightHeight = helper(node.right)

        currHeight = 1 + max(leftHeight, rightHeight)

        if abs(leftHeight - rightHeight) > 1:
            return False, currHeight

        return leftBalance and rightBalance, currHeight

    return helper(root)[0]


root = Node(1)
root.left = Node(2)
root.right = Node(3)
root.left.left = Node(4)
root.left.right = Node(5)
root.right.left = Node(6)
root.left.left.right = Node(7)

print(isBalanced(root))
