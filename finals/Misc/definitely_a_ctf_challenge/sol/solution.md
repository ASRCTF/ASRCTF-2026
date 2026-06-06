definitely_a_ctf_challenge - Solution

The problem asks for the minimum cost to partition an array into exactly K contiguous segments where each segment's cost is its maximum value. Define dp[k][i] as the minimum cost to partition the first i elements into k segments. The transition is dp[k][i] = min over j < i of dp[k-1][j] + max(h[j+1..i]), which naively runs in O(KN^2).

The key observation is that as i advances, the function max(h[j+1..i]) over j is piecewise constant and can be maintained with a monotone stack: when h[i] is processed, all j-blocks on the stack with max value <= h[i] merge into one block with value h[i]. Each merge is a range-add on the segment tree storing dp[k-1][j] + max(h[j+1..i]) over j. Critically, when j = i-1 first becomes eligible, no lazy has accumulated at that position yet, so inserting it requires only a plain point set. After all updates, dp[k][i] is a prefix-min query. This gives O(KN log N) per test case with a lazy segment tree handling range-add and range-min-query.

Running the solver on input.txt gives 33436365442.

Flag: ASRCTF{33436365442}
