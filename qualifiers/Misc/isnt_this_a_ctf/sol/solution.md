isnt_this_a_ctf - Solution

The problem asks for inversion counts across 1000 arrays of up to 10,000 elements. A brute-force O(N²) double loop would time out, so the trick is to piggyback on merge sort. During the merge of two sorted halves, whenever a right-half element is smaller than the current left-half element, it is smaller than every remaining element in the left half, so all of them form inversions with it at once. Adding the count of remaining left elements at that moment gives the full inversion count in O(N log N).

Running the solver on input.txt and summing all 1000 outputs gives 8214444935.

Flag: `ASRCTF{8214444935}`
