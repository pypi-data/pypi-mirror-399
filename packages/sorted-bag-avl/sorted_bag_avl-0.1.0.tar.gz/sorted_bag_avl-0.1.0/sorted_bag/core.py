class Node:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None
        self.height = 1
        self.size = 1
        self.freq = 1

class sorted_bag:

    def __init__(self):
        self.root = None

    def add(self, val):
        self.root = self._insert(val, self.root)

    def _insert(self, val, node):
        # new insertion
        if node is None:
            return Node(val)
        
        # val is greater than node
        if node.val < val:
            node.right = self._insert(val, node.right)
        
        # val is smaller than node
        elif node.val > val:
            node.left = self._insert(val, node.left)
        
        # val is == to node, we just increase its freq and size and return it
        else:
            node.freq += 1
            # DO NOT return early; let size/height update propagate
        
        # update height and size by getting left and right childs data
        leftchild_height = self.get_height(node.left)
        rightchild_height = self.get_height(node.right)
        leftchild_size = self.get_size(node.left)
        rightchild_size = self.get_size(node.right)
        node.height = 1 + max(leftchild_height, rightchild_height)
        node.size = node.freq + leftchild_size + rightchild_size

        # balancing check
        balance = self.get_balance(node)

        # left left:right rotation of top
        if balance > 1 and node.left and val < node.left.val:
            return self.right_rotation(node)

        # right right:left rotation of top
        elif balance < -1 and node.right and val > node.right.val:
            return self.left_rotation(node)

        # left right:left rotation of middle and right rotation of top
        elif balance > 1 and node.left and val > node.left.val:
            node.left = self.left_rotation(node.left)
            return self.right_rotation(node)

        # right left:right rotation of middle and left rotation of top
        elif balance < -1 and node.right and val < node.right.val:
            node.right = self.right_rotation(node.right)
            return self.left_rotation(node)

        # no unbalance
        else:
            return node
    

    def remove(self, val):
        self.root = self._delete(val, self.root)

    def _delete(self, val, node):
        if not node:
            return None
        
        if val<node.val:
            node.left = self._delete(val, node.left)
        elif val>node.val:
            node.right = self._delete(val, node.right)

        else:
            # found node
            if node.freq>1:
                node.freq-=1
            # else, node removal
            else:
                if not node.left:
                    return node.right
                if not node.right:
                    return node.left
                
                # inorder successor
                curr = node.right
                while curr.left:
                    curr = curr.left

                node.val = curr.val
                node.freq = curr.freq
                # we change currs freq to 1 as now it will be removed when deletion is applied on it
                curr.freq = 1
                node.right = self._delete(curr.val, node.right)

        if not node:
            return None
        # update & rebalance
        node.height = 1 + max(self.get_height(node.left),
                            self.get_height(node.right))
        node.size = node.freq + self.get_size(node.left) + self.get_size(node.right)

        balance = self.get_balance(node)

        # LL
        if balance > 1 and self.get_balance(node.left) >= 0:
            return self.right_rotation(node)
        # LR
        if balance > 1 and self.get_balance(node.left) < 0:
            node.left = self.left_rotation(node.left)
            return self.right_rotation(node)
        # RR
        if balance < -1 and self.get_balance(node.right) <= 0:
            return self.left_rotation(node)
        # RL
        if balance < -1 and self.get_balance(node.right) > 0:
            node.right = self.right_rotation(node.right)
            return self.left_rotation(node)

        return node




    
    # helper functions+++++++++++++++++++++++++++++++++++++++
    def right_rotation(self, node):
        left_child = node.left
        left_right_child = left_child.right
        left_child.right = node
        node.left = left_right_child
        # update height and sizes
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        node.size = node.freq + self.get_size(node.left) + self.get_size(node.right)
        left_child.height = 1 + max(self.get_height(left_child.left), self.get_height(left_child.right))
        left_child.size = left_child.freq + self.get_size(left_child.left) + self.get_size(left_child.right)
        return left_child

    def left_rotation(self, node):
        right_child = node.right
        right_left_child = right_child.left
        right_child.left = node
        node.right = right_left_child
        # update height and sizes
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        node.size = node.freq + self.get_size(node.left) + self.get_size(node.right)
        right_child.height = 1 + max(self.get_height(right_child.left), self.get_height(right_child.right))
        right_child.size = right_child.freq + self.get_size(right_child.left) + self.get_size(right_child.right)
        return right_child
        
    def get_balance(self, node):
        lh = self.get_height(node.left)
        rh = self.get_height(node.right)
        return lh - rh

    def get_size(self, node):
        if not node:
            return 0
        return node.size

    def get_height(self, node):
        if not node:
            return 0
        return node.height
    # IN-ORDER STRING REPRESENTATION
    def __str__(self):
        return " ".join(map(str, self._inorder(self.root)))
    
    def __repr__(self):
        if not self.root:
            return "sorted_bag()"
        # Show a few elements so the dev knows what's inside
        items = list(self)
        if len(items) > 10:
            return f"sorted_bag([{', '.join(map(str, items[:5]))}, ..., {items[-1]}], size={len(self)})"
        return f"sorted_bag({items})"
    def _inorder(self, node):
        if not node:
            return []
        
        # left subtree
        result = self._inorder(node.left)
        
        # current node, repeat value freq times
        result.extend([node.val] * node.freq)
        
        # right subtree
        result.extend(self._inorder(node.right))
        
        return result
    # general functions
    # size
    def __len__(self):
        if self.root is None:
            return 0
        return self.root.size
    # iterator
        # ITERATOR - in-order traversal
    def __iter__(self):
        yield from self._inorder_iter(self.root)

    def _inorder_iter(self, node):
        if not node:
            return
        # left subtree
        yield from self._inorder_iter(node.left)
        # current node, repeat freq times
        for _ in range(node.freq):
            yield node.val
        # right subtree
        yield from self._inorder_iter(node.right)

    # Return maximum value
    def max(self):
        node = self.root
        if not node:
            return None
        while node.right:
            node = node.right
        return node.val

    # Return minimum value
    def min(self):
        node = self.root
        if not node:
            return None
        while node.left:
            node = node.left
        return node.val

    # MEMBERSHIP CHECK
    def __contains__(self, val):
        curr = self.root
        while curr:
            if val == curr.val:
                return True
            elif val < curr.val:
                curr = curr.left
            else:
                curr = curr.right
        return False
    
    # INDEXING
    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError(f"index must be an integer, not {type(index).__name__}")
        
        length = len(self)
        
        # Support for negative indexing (e.g., tree[-1])
        if index < 0:
            index += length
            
        if index < 0 or index >= length:
            raise IndexError("series index out of range")
            
        # Your kth logic is 1-indexed (based on size), 
        # so we pass index + 1 to convert from 0-based indexing.
        return self.kth(index + 1)

    # TRUTHY/FALSY CHECK
    def __bool__(self):
        return self.root is not None

    # ORDER STATISTICS FUNCTIONS
    # COUNT LESS
    def lesser_than(self, val):
        return self._count_less(self.root, val)
    
    def _count_less(self, node, val):
        if not node:
            return 0
        if node.val>val:
            return self._count_less(node.left, val)
        elif node.val<val:
            return node.freq + self.get_size(node.left) + self._count_less(node.right, val)

        else:
            # equal case
            return self.get_size(node.left)
        
    # COUNT GREATER
    def greater_than(self, val):
        return self._count_greater(self.root, val)
    
    def _count_greater(self, node, val):
        if not node:
            return 0

        if node.val<val:
            return self._count_greater(node.right, val)
        elif node.val>val:
            return node.freq + self.get_size(node.right) + self._count_greater(node.left, val)
        else:
            return self.get_size(node.right)
        

    def kth(self, k):
        return self._kth(self.root, k)

    def _kth(self, node, k):
        if not node:
            return None
        left_size = self.get_size(node.left)
        if k <= left_size:
            return self._kth(node.left, k)
        elif k <= left_size + node.freq:
            return node.val
        else:
            return self._kth(node.right, k - left_size - node.freq)
        
    # LOWER BOUND   
    def lower_bound(self, x):
        return self._lower_bound(self.root, x)

    def _lower_bound(self, node, x):
        if not node:
            return None
        if node.val < x:
            # go right
            return self._lower_bound(node.right, x)
        else:
            # node.val >= x, could be answer, check left subtree
            left_result = self._lower_bound(node.left, x)
            return left_result if left_result is not None else node.val
    
    # UPPER BOUND
    def upper_bound(self, x):
        return self._upper_bound(self.root, x)

    def _upper_bound(self, node, x):
        if not node:
            return None
        if node.val <= x:
            # go right
            return self._upper_bound(node.right, x)
        else:
            # node.val > x, could be answer, check left subtree
            left_result = self._upper_bound(node.left, x)
            return left_result if left_result is not None else node.val

    # RANGE COUNT
    def range_count(self, l, r):
        return self.lesser_than(r+1) - self.lesser_than(l)
    # element count
    def count(self, val):
        return self._counter(self.root, val)
    def _counter(self, node, val):
        if not node:
            return 0
        if node.val<val:
            return self._counter(node.right, val)
        elif node.val>val:
            return self._counter(node.left, val)
        else:
            return node.freq
        