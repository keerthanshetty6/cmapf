# # Definition for singly-linked list.
# class ListNode(object):
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next

# list1 = ListNode(1, ListNode(2, ListNode(3)))

# while list1:
#     print(list1)  # Prints the current node
#     list1 = list1.next  # Moves to the next node

class Solution:
    def coinChange(self, coins, amount):
        """
        :type coins: List[int]
        :type amount: int
        :rtype: int
        """
        # Initialize DP array with a large value
        dp = [float('inf')] * (amount + 1)
        dp[0] = 0  # Base case: 0 coins needed for amount 0

        # Compute the minimum coins required for each amount up to `amount`
        for coin in coins:
            for i in range(coin, amount + 1):
                dp[i] = min(dp[i], dp[i - coin] + 1)
                print(coin,i,dp[i])
            print(dp)
        return dp[amount] if dp[amount] != float('inf') else -1

# Example Runs
sol = Solution()
print(sol.coinChange([1, 2, 5], 11))   # Output: 3 (5+5+1)

