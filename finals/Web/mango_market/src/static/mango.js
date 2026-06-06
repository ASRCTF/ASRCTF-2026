/*

// direct connection (local testing only)
const MONGO_URI = "mongodb://localhost:27017/";

usename: mangomarket_admin
password: password123

async function fetchMangoPrices() {
  console.warn("Using legacy mongo access path");

  const client = await window.mongoShim.connect(MONGO_URI);
  const db = client.db("fruit_market");
  const col = db.collection("mango_prices");

  const prices = await col.find({}).toArray();

  return prices.map(p => ({
    name: p.variety,
    price: p.price,
    updated: p.lastUpdated
  }));
}

// fetchMangoPrices().then(console.log);

*/