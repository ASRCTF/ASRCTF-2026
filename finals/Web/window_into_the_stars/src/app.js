const express = require('express');
const session = require('express-session');
const bodyParser = require('body-parser');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const app = express();
const port = 4567;
app.set('view engine', 'ejs');
app.set('views', __dirname);
app.use(bodyParser.urlencoded({ extended: true }));
app.use(session({
    secret: require('crypto').randomBytes(32).toString('hex'),
    resave: false,
    saveUninitialized: true,
    cookie: {
        maxAge: 1000 * 60 * 15,
        sameSite: 'lax'
    }
}));
const users = new Map(); 
const signals = new Map(); 
let nextSignalId = 1;
const ADMIN_USER = 'admin_' + require('crypto').randomBytes(8).toString('hex');
const ADMIN_PASS = require('crypto').randomBytes(16).toString('hex');
users.set(ADMIN_USER, ADMIN_PASS);
signals.set(ADMIN_USER, []);
let flag = "flag{dummy_flag}";
try {
    flag = fs.readFileSync('/flag.txt', 'utf8').trim();
} catch (e) {
    try {
        flag = fs.readFileSync('../sol/flag.txt', 'utf8').trim();
    } catch(e2) {
        console.log("Could not read flag file, using dummy");
    }
}
signals.get(ADMIN_USER).push({ id: nextSignalId++, title: "URGENT INTERCEPT", content: flag });
app.get('/', (req, res) => {
    res.render('index', { user: req.session.user });
});
app.get('/login', (req, res) => {
    res.render('login', { error: null });
});
app.post('/login', (req, res) => {
    const { username, password } = req.body;
    if (users.has(username) && users.get(username) === password) {
        req.session.user = username;
        return res.redirect('/dashboard');
    }
    if (!users.has(username)) {
        users.set(username, password);
        signals.set(username, []);
        req.session.user = username;
        return res.redirect('/dashboard');
    }
    res.render('login', { error: 'Invalid credentials.' });
});
app.get('/logout', (req, res) => {
    req.session.destroy();
    res.redirect('/');
});
app.get('/dashboard', (req, res) => {
    if (!req.session.user) return res.redirect('/login');
    const userSignals = signals.get(req.session.user) || [];
    res.render('dashboard', { user: req.session.user, signals: userSignals });
});
app.post('/dashboard', (req, res) => {
    if (!req.session.user) return res.redirect('/login');
    const { title, content } = req.body;
    if (title && content) {
        const userSignals = signals.get(req.session.user);
        userSignals.push({ id: nextSignalId++, title, content });
    }
    res.redirect('/dashboard');
});
app.get('/search', (req, res) => {
    if (!req.session.user) return res.status(401).send("Unauthorized");
    const q = req.query.q || '';
    const userSignals = signals.get(req.session.user) || [];
    const results = userSignals.filter(s => s.content.includes(q) || s.title.includes(q));
    res.render('search', { query: q, results });
});
app.get('/spectrogram/:id', (req, res) => {
    if (!req.session.user) return res.status(401).send("Unauthorized");
    const id = parseInt(req.params.id);
    const userSignals = signals.get(req.session.user) || [];
    const signal = userSignals.find(s => s.id === id);
    if (!signal) return res.status(404).send("Not found");
    res.render('spectrogram', { signal });
});
app.get('/report', (req, res) => {
    res.render('report', { message: null });
});
app.post('/report', (req, res) => {
    const url = req.body.url;
    if (!url || !url.startsWith('http')) {
        return res.render('report', { message: 'Invalid URL. Must start with http:
    }
    try {
        spawn('node', ['bot.js', url, ADMIN_USER, ADMIN_PASS], { detached: true, stdio: 'ignore' });
        res.render('report', { message: 'Lead Researcher is reviewing your signal intercept.' });
    } catch (e) {
        console.error(e);
        res.render('report', { message: 'Failed to contact Lead Researcher.' });
    }
});
app.listen(port, '0.0.0.0', () => {
    console.log(`Deep Space Signals listening on port ${port}`);
});
