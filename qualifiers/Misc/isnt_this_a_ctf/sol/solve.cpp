#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

ll merge_count(vector<int>& a, int l, int r) {
    if (r - l <= 1) return 0;
    int m = (l + r) / 2;
    ll cnt = merge_count(a, l, m) + merge_count(a, m, r);
    vector<int> tmp;
    int i = l, j = m;
    while (i < m && j < r) {
        if (a[i] <= a[j]) tmp.push_back(a[i++]);
        else { cnt += m - i; tmp.push_back(a[j++]); }
    }
    while (i < m) tmp.push_back(a[i++]);
    while (j < r) tmp.push_back(a[j++]);
    for (int k = l; k < r; ++k) a[k] = tmp[k - l];
    return cnt;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int T; cin >> T;
    ll total = 0;
    while (T--) {
        int n; cin >> n;
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        ll inv = merge_count(a, 0, n);
        cout << inv << "\n";
        total += inv;
    }
    return 0;
}
