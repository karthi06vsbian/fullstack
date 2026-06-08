import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  CreditCard,
  LayoutDashboard,
  MessageCircle,
  Minus,
  PackageCheck,
  Plus,
  Search,
  ShoppingCart,
  Truck,
  Zap,
} from "lucide-react";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000/api";
const MEDIA_BASE = API_BASE.replace("/api", "");
const WHATSAPP_NUMBER = "919944823602";
const PRODUCT_SUPPORT_NUMBER = "99448 23602";
const CREDIT_CONTACT_NUMBER = "87786 06059";
const INSTAGRAM_ID = "kxrxtxi__";

const fallbackProducts = [
  { id: 1, name: "Mini Me Custom Figure", category: "Mini Me", price: 1499, rating: 4.9, image: "/productsimg/minime.jpg", material: "Resin / PLA", weight_grams: 350, is_featured: true, is_custom: true, description: "Custom lifelike miniature from your photo." },
  { id: 2, name: "Name Keychain", category: "Keychains", price: 179, rating: 4.8, image: "/productsimg/keychains/keychain1.jpg", material: "PLA", weight_grams: 80, is_featured: true, description: "Personalized lightweight name keychain." },
  { id: 3, name: "Desk Planter", category: "Home Decor", price: 499, rating: 4.9, image: "/productsimg/home-decor/desk-planter.jpg", material: "Matte PLA", weight_grams: 420, is_featured: true, description: "Modern planter for desks and shelves." },
  { id: 4, name: "Fidget Toy V2", category: "Toys", price: 279, rating: 4.8, image: "/productsimg/toys/fidget-toy-v2-cut.jpg", material: "PETG", weight_grams: 180, is_featured: true, description: "Smooth articulated fidget print." },
];

function rupees(amount) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount || 0);
}

function localShippingQuote(pincode, weight = 250, subtotal = 0, paymentMethod = "razorpay") {
  const clean = String(pincode).replace(/\D/g, "");
  if (clean.length !== 6) throw new Error("Enter a valid 6 digit Indian pincode.");
  const zones = [
    ["641", "Coimbatore local", 45, 1],
    ["642", "Coimbatore region", 55, 1],
    ["643", "Nilgiris / nearby", 75, 2],
    ["6", "South India", 95, 3],
    ["5", "South India", 110, 4],
    ["4", "West India", 135, 5],
    ["3", "West / North India", 145, 6],
    ["2", "North India", 155, 7],
    ["1", "North India", 165, 7],
    ["7", "East India", 175, 8],
    ["8", "East India", 185, 8],
  ];
  const match = zones.find(([prefix]) => clean.startsWith(prefix)) || ["", "Remote India", 210, 9];
  const extraBlocks = Math.max(0, Math.ceil((Math.max(weight, 250) - 500) / 500));
  const shipping = subtotal >= 2499 ? 0 : match[2] + extraBlocks * 35;
  const codCharge = paymentMethod === "cod" ? Math.max(45, Math.round(subtotal * 0.02)) : 0;
  return {
    hub: "Coimbatore",
    hub_pincode: "641001",
    destination_pincode: clean,
    zone: match[1],
    shipping_charge: shipping,
    cod_charge: codCharge,
    total_delivery_charge: shipping + codCharge,
    estimated_days: match[3],
    service: paymentMethod === "cod" ? "Shiprocket Express COD" : "Shiprocket Express",
    free_shipping_applied: shipping === 0,
    dev_mode: true,
  };
}

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}

function App() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [activeCategory, setActiveCategory] = useState("Top Selling");
  const [query, setQuery] = useState("");
  const [cart, setCart] = useState([]);
  const [checkoutOpen, setCheckoutOpen] = useState(false);
  const [adminOpen, setAdminOpen] = useState(false);
  const [quote, setQuote] = useState(null);
  const [notice, setNotice] = useState("");

  useEffect(() => {
    api("/products/")
      .then((data) => {
        setProducts(data.products);
        setCategories(["Top Selling", "All", ...data.categories.filter((category) => category !== "Mini Me")]);
      })
      .catch(() => {
        setProducts(fallbackProducts);
        setCategories(["Top Selling", "All", "Keychains", "Home Decor", "Toys"]);
        setNotice("Backend offline: showing demo catalog.");
      });
  }, []);

  const topSellingProducts = useMemo(() => {
    const normalProducts = products.filter((product) => product.category !== "Mini Me");
    const featured = normalProducts.filter((product) => product.is_featured || product.is_custom);
    return (featured.length ? featured : normalProducts).slice(0, 5);
  }, [products]);

  const filtered = useMemo(() => {
    if (activeCategory === "Top Selling") return topSellingProducts;
    return products.filter((product) => {
      if (product.category === "Mini Me") return false;
      const categoryMatch = activeCategory === "All" || product.category === activeCategory;
      const searchMatch = product.name.toLowerCase().includes(query.toLowerCase()) || product.category.toLowerCase().includes(query.toLowerCase());
      return categoryMatch && searchMatch;
    });
  }, [products, activeCategory, query, topSellingProducts]);

  const totals = useMemo(() => {
    const subtotal = cart.reduce((sum, item) => sum + item.product.price * item.quantity, 0);
    const weight = cart.reduce((sum, item) => sum + item.product.weight_grams * item.quantity, 0);
    const shipping = quote?.total_delivery_charge ?? quote?.shipping_charge ?? 0;
    return { subtotal, weight, shipping, total: subtotal + shipping };
  }, [cart, quote]);

  const miniMe = products.find((product) => product.category === "Mini Me") || fallbackProducts[0];

  function addToCart(product, quantity = 1) {
    setCart((current) => {
      const existing = current.find((item) => item.product.id === product.id);
      if (existing) return current.map((item) => item.product.id === product.id ? { ...item, quantity: item.quantity + quantity } : item);
      return [...current, { product, quantity, custom_note: "" }];
    });
    setNotice(`${product.name} added to cart.`);
  }

  function updateQty(productId, quantity) {
    setCart((current) => current.map((item) => item.product.id === productId ? { ...item, quantity: Math.max(1, quantity) } : item));
  }

  function buyNow(product) {
    addToCart(product);
    setCheckoutOpen(true);
  }

  return (
    <div>
      <OfferTicker />
      <Nav cartCount={cart.reduce((sum, item) => sum + item.quantity, 0)} onCart={() => setCheckoutOpen(true)} onAdmin={() => setAdminOpen(true)} />
      {notice && <div className="notice">{notice}</div>}
      <Hero onShop={() => document.getElementById("shop")?.scrollIntoView({ behavior: "smooth" })} />
      <main>
        <section className="service-band">
          <Feature icon={<Truck />} title="Coimbatore Hub" text="Shipping starts from pincode 641001 and adjusts by destination pincode." />
          <Feature icon={<CreditCard />} title="Razorpay Checkout" text="Prepaid order flow ready for live keys." />
          <Feature icon={<PackageCheck />} title="Shiprocket Delivery" text="Shipment creation hooks are wired after payment verification." />
          <Feature icon={<MessageCircle />} title="WhatsApp Support" text="Custom print help and fast order support." />
        </section>
        <section id="shop" className="shop-shell">
          <MiniMeSpotlight product={miniMe} />
          <div className="shop-toolbar">
            <div>
              <p className="eyebrow">Full Ecommerce Catalog</p>
              <h2>Shop ready prints or customize your own.</h2>
            </div>
            <div className="search">
              <Search size={18} />
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search products" />
            </div>
          </div>
          <div className="category-tabs">
            {categories.map((category) => (
              <button key={category} className={activeCategory === category ? "active" : ""} onClick={() => setActiveCategory(category)}>
                {category}
              </button>
            ))}
          </div>
          <div className="product-grid">
            {filtered.map((product) => (
              <ProductCard key={product.id} product={product} onAdd={addToCart} onBuy={buyNow} />
            ))}
          </div>
        </section>
        <Reviews />
      </main>
      <SiteFooter />
      <FloatingWhatsApp />
      {checkoutOpen && (
        <Checkout
          cart={cart}
          totals={totals}
          quote={quote}
          setQuote={setQuote}
          updateQty={updateQty}
          onClose={() => setCheckoutOpen(false)}
          onClear={() => setCart([])}
        />
      )}
      {adminOpen && <AdminDashboard onClose={() => setAdminOpen(false)} onProductUpdated={(updated) => setProducts((items) => items.map((item) => item.id === updated.id ? updated : item))} />}
    </div>
  );
}

function OfferTicker() {
  const text = "🎉 All products up to 50% discount  🚚 Fast Shiprocket delivery  💳 Razorpay + COD available  🔥 Weekend combo offers  🎁 Custom gifts on WhatsApp";
  return (
    <div className="offer-ticker">
      <div className="offer-track"><span>{text}</span><span>{text}</span></div>
    </div>
  );
}

function Nav({ cartCount, onCart, onAdmin }) {
  return (
    <nav className="nav">
      <a className="logo" href="#">PrintForge<span> 3D</span></a>
      <div className="nav-links">
        <a href="#shop">Shop</a>
        <button className="admin-link" onClick={onAdmin}><LayoutDashboard size={18} /> Admin</button>
        <a href={`https://wa.me/${WHATSAPP_NUMBER}?text=Hi%20PrintForge%2C%20I%20want%20a%20custom%203D%20print.`} target="_blank" rel="noreferrer">Customize</a>
        <button className="cart-button" onClick={onCart} title="Open cart">
          <ShoppingCart size={20} />
          {cartCount > 0 && <span>{cartCount}</span>}
        </button>
      </div>
    </nav>
  );
}

function MiniMeSpotlight({ product }) {
  return (
    <section className="mini-spotlight">
      <div className="mini-copy">
        <p className="eyebrow">✨ Fully Customized Mini Me</p>
        <h2>Turn your photo into a personalized 3D miniature.</h2>
        <p>No fixed price for this one: every Mini Me is custom made by size, pose, finish, and photo quality. Send your image on WhatsApp and we will confirm the design and quote.</p>
        <a className="btn ghost" href={`https://wa.me/${WHATSAPP_NUMBER}?text=Hi%20PrintForge%2C%20I%20want%20a%20fully%20customized%20Mini%20Me%203D%20model.`} target="_blank" rel="noreferrer">
          <MessageCircle size={18} /> Buy on WhatsApp
        </a>
      </div>
      <div className="mini-media">
        <img src={imageUrl(product.image)} alt="Mini Me custom 3D model" />
      </div>
    </section>
  );
}

function Hero({ onShop }) {
  return (
    <header className="hero">
      <video autoPlay muted loop playsInline poster="https://images.unsplash.com/photo-1631378426482-54edfe73115b?auto=format&fit=crop&w=2200&q=82">
        <source src={`${MEDIA_BASE}/assets/video/3d-printer-entrance.mp4`} type="video/mp4" />
      </video>
      <div className="hero-copy">
        <p className="eyebrow">Premium 3D Printing Studio</p>
        <h1>PrintForge</h1>
        <p>Buy 3D printed products, enter your pincode for delivery charges, pay with Razorpay, and get fast delivery through Shiprocket.</p>
        <div className="hero-actions">
          <button className="btn" onClick={onShop}><Zap size={18} /> Shop Now</button>
          <a className="btn ghost" href={`https://wa.me/${WHATSAPP_NUMBER}?text=Hi%20PrintForge%2C%20I%20want%20to%20customize%20a%203D%20printed%20product.`} target="_blank" rel="noreferrer"><MessageCircle size={18} /> WhatsApp</a>
        </div>
      </div>
    </header>
  );
}

function Feature({ icon, title, text }) {
  return <article><div>{icon}</div><h3>{title}</h3><p>{text}</p></article>;
}

function imageUrl(path) {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  if (path.startsWith("/media") || path.startsWith("/productsimg")) return `${MEDIA_BASE}${path}`;
  return path;
}

function ProductCard({ product, onAdd, onBuy }) {
  return (
    <article className="product-card">
      <div className="product-image">
        <img src={imageUrl(product.image)} alt={product.name} loading="lazy" />
        {product.is_custom && <span className="pill">Custom</span>}
      </div>
      <div className="product-body">
        <div>
          <p>{product.category} · {product.material}</p>
          <h3>{product.name}</h3>
        </div>
        <p className="description">{product.description}</p>
        <div className="product-meta">
          <strong>{rupees(product.price)}</strong>
          <span>★ {product.rating}</span>
        </div>
        <div className="card-actions">
          <button className="btn secondary" onClick={() => onAdd(product)}>Add</button>
          <button className="btn" onClick={() => onBuy(product)}>Buy Now</button>
        </div>
      </div>
    </article>
  );
}

function Checkout({ cart, totals, quote, setQuote, updateQty, onClose, onClear }) {
  const [customer, setCustomer] = useState({ name: "", email: "", phone: "", address_line: "", city: "", state: "Tamil Nadu", pincode: "" });
  const [paymentMethod, setPaymentMethod] = useState("");
  const [loading, setLoading] = useState(false);
  const [shippingLoading, setShippingLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const addressReady = Boolean(
    cart.length &&
    customer.address_line.trim() &&
    customer.city.trim() &&
    customer.state.trim() &&
    /^\d{6}$/.test(customer.pincode.trim())
  );

  useEffect(() => {
    if (!addressReady || !paymentMethod || successMessage) return;
    const timer = window.setTimeout(() => {
      getQuote({ silent: true });
    }, 450);
    return () => window.clearTimeout(timer);
  }, [addressReady, customer.address_line, customer.city, customer.state, customer.pincode, paymentMethod, totals.subtotal, totals.weight, successMessage]);

  async function getQuote(options = {}) {
    const { silent = false } = options;
    setShippingLoading(true);
    if (!silent) setMessage("");
    try {
      const data = await api("/shipping/", { method: "POST", body: JSON.stringify({ pincode: customer.pincode, weight_grams: totals.weight, subtotal: totals.subtotal, payment_method: paymentMethod }) });
      setQuote(data);
    } catch (error) {
      try {
        const localQuote = localShippingQuote(customer.pincode, totals.weight, totals.subtotal, paymentMethod);
        setQuote(localQuote);
        if (!silent) setMessage("Backend offline: showing demo shipping calculation.");
      } catch (quoteError) {
        if (!silent) setMessage(quoteError.message || error.message);
      }
    } finally {
      setShippingLoading(false);
    }
  }

  function showOrderSuccess(orderId) {
    setSuccessMessage(`Order PF-${orderId} successfully placed. Your tracking ID will be shared through WhatsApp.`);
    setMessage("");
    onClear();
  }

  async function placeOrder() {
    if (!paymentMethod) {
      setMessage("Choose Razorpay or Cash on Delivery to place the order.");
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      if (!quote) await getQuote();
      const data = await api("/orders/", {
        method: "POST",
        body: JSON.stringify({
          customer,
          payment_method: paymentMethod,
          items: cart.map((item) => ({ product_id: item.product.id, quantity: item.quantity, custom_note: item.custom_note })),
        }),
      });
      if (paymentMethod === "cod") {
        showOrderSuccess(data.order.id);
      } else if (window.Razorpay && data.razorpay.key) {
        const gateway = new window.Razorpay({
          key: data.razorpay.key,
          amount: data.razorpay.amount,
          currency: "INR",
          name: "PrintForge",
          description: "3D printed products",
          order_id: data.razorpay.order_id,
          handler: async (response) => {
            await api("/payments/verify/", {
              method: "POST",
              body: JSON.stringify({ order_id: data.order.id, ...response }),
            });
            showOrderSuccess(data.order.id);
          },
          prefill: { name: customer.name, email: customer.email, contact: customer.phone },
        });
        gateway.open();
      } else {
        setMessage("Online payment is not configured yet. Add Razorpay keys in backend/.env, restart Django, and try Razorpay again.");
      }
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="drawer-backdrop">
      <aside className="checkout-drawer">
        <div className="drawer-head">
          <div><p className="eyebrow">Checkout</p><h2>Cart & Delivery</h2></div>
          <button onClick={onClose} className="close">×</button>
        </div>
        {successMessage ? (
          <div className="success-panel">
            <PackageCheck size={34} />
            <h3>Order Placed</h3>
            <p>{successMessage}</p>
            <button className="btn wide-button" onClick={onClose}>Done</button>
          </div>
        ) : cart.length === 0 ? <p className="empty">Your cart is empty.</p> : (
          <>
            <div className="cart-lines">
              {cart.map((item) => (
                <div className="cart-line" key={item.product.id}>
                  <img src={imageUrl(item.product.image)} alt={item.product.name} />
                  <div>
                    <strong>{item.product.name}</strong>
                    <span>{rupees(item.product.price)}</span>
                    <div className="stepper">
                      <button onClick={() => updateQty(item.product.id, item.quantity - 1)}><Minus size={14} /></button>
                      <b>{item.quantity}</b>
                      <button onClick={() => updateQty(item.product.id, item.quantity + 1)}><Plus size={14} /></button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="form-grid">
              {["name", "email", "phone", "address_line", "city", "state", "pincode"].map((field) => (
                <label key={field} className={field === "address_line" ? "wide" : ""}>
                  {field.replace("_", " ")}
                  <input value={customer[field]} onChange={(event) => { setCustomer({ ...customer, [field]: event.target.value }); setQuote(null); }} />
                </label>
              ))}
            </div>
            <div className="payment-toggle">
              <button className={paymentMethod === "razorpay" ? "active" : ""} onClick={() => { setPaymentMethod("razorpay"); setQuote(null); }}>
                <CreditCard size={17} /> Razorpay
              </button>
              <button className={paymentMethod === "cod" ? "active" : ""} onClick={() => { setPaymentMethod("cod"); setQuote(null); }}>
                <PackageCheck size={17} /> Cash on Delivery
              </button>
            </div>
            {!paymentMethod && <div className="quote muted-quote">Choose Razorpay or Cash on Delivery to continue.</div>}
            {addressReady && paymentMethod && !quote && !shippingLoading && <div className="quote muted-quote">Shipping will be calculated automatically from your address.</div>}
            {shippingLoading && <div className="quote muted-quote"><Truck size={16} /> Calculating shipping from your address...</div>}
            {quote && <div className="quote">From {quote.hub} to {quote.destination_pincode}: shipping {rupees(quote.shipping_charge)}{quote.cod_charge ? ` + COD ${rupees(quote.cod_charge)}` : ""} · {quote.estimated_days} day delivery by {quote.service}</div>}
            <div className="totals">
              <span>Subtotal <b>{rupees(totals.subtotal)}</b></span>
              <span>Shipping <b>{rupees(totals.shipping)}</b></span>
              <span>Total <b>{rupees(totals.total)}</b></span>
            </div>
            {message && <div className="message">{message}</div>}
            <button className="btn wide-button" onClick={placeOrder} disabled={loading || !paymentMethod}>
              {paymentMethod === "cod" ? <PackageCheck size={18} /> : <CreditCard size={18} />}
              {!paymentMethod ? "Choose Payment Method" : paymentMethod === "cod" ? "Place COD Order" : "Pay with Razorpay"}
            </button>
          </>
        )}
      </aside>
    </div>
  );
}

function Reviews() {
  const reviews = [
    { name: "Karthik R", text: "The custom keychains looked sharp, and the WhatsApp updates made the whole order easy.", rating: "★★★★★" },
    { name: "Divya S", text: "I ordered a project model for college. Print quality was clean and delivery from Coimbatore was fast.", rating: "★★★★★" },
    { name: "Mohammed A", text: "Mini Me customization was handled nicely. They helped with size, finish, and final look before printing.", rating: "★★★★★" },
  ];
  return (
    <section className="reviews-section">
      <div className="reviews-head">
        <p className="eyebrow">Customer Reviews</p>
        <h2>Custom orders, real smiles.</h2>
      </div>
      <div className="reviews-grid">
        {reviews.map((review) => (
          <article className="review-card" key={review.name}>
            <strong>{review.rating}</strong>
            <p>{review.text}</p>
            <span>{review.name}</span>
          </article>
        ))}
      </div>
    </section>
  );
}

function SiteFooter() {
  const year = new Date().getFullYear();
  return (
    <footer className="site-footer">
      <div>
        <h2>PrintForge 3D</h2>
        <p>Premium 3D printed products, custom Mini Me models, keychains, toys, useful appliances, projects, home decor, and fast delivery support.</p>
      </div>
      <div>
        <h3>Contact</h3>
        <a href={`https://wa.me/${WHATSAPP_NUMBER}?text=Hi%20PrintForge%2C%20I%20need%20help%20with%20a%203D%20print%20order.`} target="_blank" rel="noreferrer">Orders WhatsApp: +91 {PRODUCT_SUPPORT_NUMBER}</a>
        <a href={`https://www.instagram.com/${INSTAGRAM_ID}/`} target="_blank" rel="noreferrer">Instagram: @{INSTAGRAM_ID}</a>
        <span>Product Support: +91 {PRODUCT_SUPPORT_NUMBER}</span>
        <span>Hub: Coimbatore, Tamil Nadu</span>
      </div>
      <div>
        <h3>Credits</h3>
        <p>This website is built by Karthikeyan B.E CSE.</p>
        <p>Contact: +91 {CREDIT_CONTACT_NUMBER}</p>
        <p>Instagram: @{INSTAGRAM_ID}</p>
        <p>© {year} PrintForge. All rights reserved.</p>
      </div>
    </footer>
  );
}

function AdminDashboard({ onClose, onProductUpdated }) {
  const [summary, setSummary] = useState(null);
  const [password, setPassword] = useState(localStorage.getItem("printforgeAdminPassword") || "");
  const [authed, setAuthed] = useState(false);
  const [error, setError] = useState("");
  const [savingId, setSavingId] = useState(null);

  async function loadAdmin(pass = password) {
    setError("");
    const cleanPassword = String(pass || "").trim();
    if (!cleanPassword) {
      setError("Please enter the admin password.");
      return;
    }
    try {
      const data = await api("/admin/summary/", { headers: { "X-Admin-Password": cleanPassword } });
      setSummary(data);
      setAuthed(true);
      setPassword(cleanPassword);
      localStorage.setItem("printforgeAdminPassword", cleanPassword);
    } catch (err) {
      setAuthed(false);
      localStorage.removeItem("printforgeAdminPassword");
      setError(err.message || "Admin API is unavailable. Start Django + MySQL to view live orders.");
    }
  }

  useEffect(() => {
    if (password) loadAdmin(password);
  }, []);

  function updateProductDraft(productId, field, value) {
    setSummary((current) => ({
      ...current,
      products: current.products.map((product) => product.id === productId ? { ...product, [field]: value } : product),
    }));
  }

  async function saveProduct(product) {
    setSavingId(product.id);
    setError("");
    try {
      const data = await api(`/admin/products/${product.id}/`, {
        method: "POST",
        headers: { "X-Admin-Password": password },
        body: JSON.stringify({ name: product.name, price: product.price }),
      });
      setSummary((current) => ({
        ...current,
        products: current.products.map((item) => item.id === data.product.id ? data.product : item),
      }));
      onProductUpdated(data.product);
    } catch (err) {
      setError(err.message || "Could not save product.");
    } finally {
      setSavingId(null);
    }
  }

  const stats = summary?.stats || { orders: 0, revenue: 0, products: 0, cod_orders: 0, razorpay_orders: 0 };
  const orders = summary?.recent_orders || [];
  const editableProducts = summary?.products || [];

  return (
    <div className="drawer-backdrop">
      <aside className="admin-drawer">
        <div className="drawer-head">
          <div><p className="eyebrow">Admin</p><h2>Orders & Store Details</h2></div>
          <button onClick={onClose} className="close">×</button>
        </div>
        {error && <div className="message">{error}</div>}
        {!authed ? (
          <div className="admin-login">
            <label>
              Admin password
              <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") loadAdmin(password); }} placeholder="Enter admin password" />
            </label>
            <button className="btn wide-button" onClick={() => loadAdmin(password)}>Login</button>
            <p>Default local password is `admin123`. Change it in backend/.env with ADMIN_PANEL_PASSWORD.</p>
          </div>
        ) : (
          <>
          <div className="admin-stats">
            <Stat label="Orders" value={stats.orders} />
            <Stat label="Revenue" value={rupees(stats.revenue)} />
            <Stat label="Products" value={stats.products} />
            <Stat label="COD Orders" value={stats.cod_orders} />
            <Stat label="Razorpay" value={stats.razorpay_orders} />
          </div>
          <div className="admin-section">
            <h3>Recent Orders</h3>
            <div className="admin-table">
              {orders.length === 0 ? <p className="empty">No orders yet.</p> : orders.map((order) => (
                <article key={order.id} className="admin-order">
                  <div>
                    <strong>{order.order_number}</strong>
                    <span>{order.customer_name} · {order.phone}</span>
                    <small>{order.address_line}, {order.city}, {order.state} - {order.pincode}</small>
                  </div>
                  <div>
                    <b>{rupees(order.total)}</b>
                    <span>{order.payment_method.toUpperCase()} · {order.status}</span>
                  </div>
                </article>
              ))}
            </div>
          </div>
          <div className="admin-section">
            <h3>Products by Category</h3>
            <div className="category-report">
              {(summary?.category_counts || []).map((item) => <span key={item.category}>{item.category}: <b>{item.count}</b></span>)}
            </div>
          </div>
          <div className="admin-section">
            <h3>Edit Products</h3>
            <div className="product-editor-list">
              {editableProducts.map((product) => (
                <article className="product-editor" key={product.id}>
                  <img src={imageUrl(product.image)} alt={product.name} />
                  <label>
                    Name
                    <input value={product.name} onChange={(event) => updateProductDraft(product.id, "name", event.target.value)} />
                  </label>
                  <label>
                    Price
                    <input type="number" min="0" value={product.price} onChange={(event) => updateProductDraft(product.id, "price", event.target.value)} />
                  </label>
                  <button className="btn secondary" onClick={() => saveProduct(product)} disabled={savingId === product.id}>
                    {savingId === product.id ? "Saving" : "Save"}
                  </button>
                </article>
              ))}
            </div>
          </div>
          </>
        )}
      </aside>
    </div>
  );
}

function Stat({ label, value }) {
  return <article><span>{label}</span><strong>{value}</strong></article>;
}

function FloatingWhatsApp() {
  return (
    <a className="whatsapp-float" href={`https://wa.me/${WHATSAPP_NUMBER}?text=Hi%20PrintForge%2C%20I%20need%20help%20with%20delivery%20or%20customization.`} target="_blank" rel="noreferrer" title="Contact on WhatsApp">
      <MessageCircle size={24} />
    </a>
  );
}

createRoot(document.getElementById("root")).render(<App />);
