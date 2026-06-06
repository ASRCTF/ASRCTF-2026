#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const ll INF = 1e18;

struct Seg {
    int n;
    vector<ll> mn, lz;
    Seg(int n) : n(n), mn(4*n, INF), lz(4*n, 0) {}
    void push(int v, int lo, int hi) {
        if (lz[v] && lo < hi) {
            for (int c : {2*v, 2*v+1}) {
                lz[c] += lz[v];
                if (mn[c] < INF) mn[c] += lz[v];
            }
            lz[v] = 0;
        }
    }
    void set_pt(int p, ll val, int v, int lo, int hi) {
        if (lo == hi) { mn[v] = val; return; }
        push(v, lo, hi);
        int m = (lo + hi) / 2;
        p <= m ? set_pt(p, val, 2*v, lo, m) : set_pt(p, val, 2*v+1, m+1, hi);
        mn[v] = min(mn[2*v], mn[2*v+1]);
    }
    void add(int l, int r, ll x, int v, int lo, int hi) {
        if (r < lo || hi < l) return;
        if (l <= lo && hi <= r) { if (mn[v] < INF) mn[v] += x; lz[v] += x; return; }
        push(v, lo, hi); int m = (lo + hi) / 2;
        add(l, r, x, 2*v, lo, m); add(l, r, x, 2*v+1, m+1, hi);
        mn[v] = min(mn[2*v], mn[2*v+1]);
    }
    ll qmin(int l, int r, int v, int lo, int hi) {
        if (r < lo || hi < l) return INF;
        if (l <= lo && hi <= r) return mn[v];
        push(v, lo, hi); int m = (lo + hi) / 2;
        return min(qmin(l, r, 2*v, lo, m), qmin(l, r, 2*v+1, m+1, hi));
    }
    void set_pt(int p, ll val) { set_pt(p, val, 1, 0, n-1); }
    void add(int l, int r, ll x) { if (l <= r) add(l, r, x, 1, 0, n-1); }
    ll qmin(int l, int r) { if (l > r) return INF; return qmin(l, r, 1, 0, n-1); }
};

ll solve(vector<int>& h, int K) {
    int N = h.size();
    vector<ll> prev(N + 1, INF);
    prev[0] = 0;
    for (int k = 1; k <= K; k++) {
        Seg seg(N);
        vector<ll> cur(N + 1, INF);
        vector<pair<int,int>> stk;
        for (int i = 1; i <= N; i++) {
            int hi = h[i-1], j = i-1, left = j;
            while (!stk.empty() && stk.back().first <= hi) {
                auto [val, l] = stk.back(); stk.pop_back();
                seg.add(l, left-1, hi - val);
                left = l;
            }
            if (prev[j] < INF) seg.set_pt(j, prev[j]);
            seg.add(j, j, hi);
            stk.push_back({hi, left});
            cur[i] = seg.qmin(0, j);
        }
        prev = cur;
    }
    return prev[N];
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int T; cin >> T;
    ll total = 0;
    while (T--) {
        int N, K; cin >> N >> K;
        vector<int> h(N);
        for (auto& x : h) cin >> x;
        total += solve(h, K);
    }
    cout << total << "\n";
    return 0;
}
