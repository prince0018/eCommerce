const state = {
  products: [],
  category: "All",
  search: "",
  sort: "featured",
  token: localStorage.getItem("cg_token"),
  user: JSON.parse(localStorage.getItem("cg_user") || "null"),
  cart: { items: [], total_items: 0, total_amount: 0, currency: "INR" },
  authMode: "login",
};

const categoryStyles = {
  Mobiles: ["M", "#b9d7ff"], Laptops: ["L", "#d6d1ff"], Audio: ["A", "#ffc7bc"],
  Accessories: ["+", "#f4d76b"], Furniture: ["F", "#bed9c8"], Monitors: ["▣", "#c4dce3"],
  Storage: ["S", "#e0d0bd"], Networking: ["N", "#bfd7d3"], Wearables: ["W", "#e8c7db"],
  Power: ["P", "#f5c9a8"], Bags: ["B", "#d5c7ad"], Footwear: ["R", "#c5d8ff"],
  Clothing: ["C", "#efc3bc"], Kitchen: ["K", "#d0dfb7"], Fitness: ["G", "#b8d8cf"],
  Stationery: ["✎", "#f0d69d"],
};

const $ = (selector) => document.querySelector(selector);
const money = (value, currency = "INR") =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency, maximumFractionDigits: 0 }).format(value);
const authHeaders = () => state.token ? { Authorization: `Bearer ${state.token}` } : {};

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...authHeaders(), ...(options.headers || {}) },
  });
  if (response.status === 204) return null;
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || "Something went wrong");
  return body;
}

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.classList.remove("show"), 2600);
}

function refreshIcons() {
  if (window.lucide) window.lucide.createIcons();
}

async function loadProducts() {
  const data = await api("/products");
  state.products = data.products;
  renderHeroProducts();
  renderCategories();
  renderProducts();
}

function renderHeroProducts() {
  const featured = [...state.products]
    .filter((product) => product.thumbnail)
    .sort((a, b) => (Number(b.rating || 0) - Number(a.rating || 0)) || (Number(b.discount_percentage || 0) - Number(a.discount_percentage || 0)))
    .slice(0, 3);

  const [main, smallOne, smallTwo] = featured;
  renderHeroCard("#heroMain", main, true);
  renderHeroCard("#heroSmallOne", smallOne, false);
  renderHeroCard("#heroSmallTwo", smallTwo, false);

  const productCount = state.products.length;
  const averageRating = state.products.reduce((total, product) => total + Number(product.rating || 0), 0) / productCount;
  const proofItems = document.querySelectorAll(".hero-proof strong");
  if (proofItems[0]) proofItems[0].textContent = productCount;
  if (proofItems[1]) proofItems[1].textContent = averageRating.toFixed(1);
}

function renderHeroCard(selector, product, showCopy) {
  const element = $(selector);
  if (!element || !product) return;
  element.style.setProperty("--hero-bg", (categoryStyles[product.category] || ["", "#d8d5cc"])[1]);
  element.innerHTML = `
    <img src="${product.thumbnail}" alt="${product.name}">
    ${showCopy ? `<div class="hero-product-copy">
      <span>${product.category}</span>
      <strong>${product.name}</strong>
    </div>` : `<span class="hero-mini-label">${product.name}</span>`}
  `;
}

function renderCategories() {
  const categories = ["All", ...new Set(state.products.map((product) => product.category))];
  $("#categoryStrip").innerHTML = categories.map((category) => `
    <button class="category-chip ${state.category === category ? "active" : ""}"
      data-category="${category}" type="button">${category}</button>
  `).join("");
}

function visibleProducts() {
  const query = state.search.toLowerCase();
  const products = state.products.filter((product) => {
    const categoryMatch = state.category === "All" || product.category === state.category;
    const textMatch = !query || `${product.name} ${product.description} ${product.brand}`.toLowerCase().includes(query);
    return categoryMatch && textMatch;
  });
  return products.sort((a, b) => {
    if (state.sort === "price-low") return Number(a.price) - Number(b.price);
    if (state.sort === "price-high") return Number(b.price) - Number(a.price);
    if (state.sort === "rating") return Number(b.rating || 0) - Number(a.rating || 0);
    if (state.sort === "name") return a.name.localeCompare(b.name);
    return a.id - b.id;
  });
}

function productVisual(product, extraClass = "") {
  const [symbol, color] = categoryStyles[product.category] || ["•", "#d8d5cc"];
  return `<div class="product-visual ${extraClass}" style="--card-color:${color}" data-symbol="${symbol}">
    ${product.thumbnail ? `<img src="${product.thumbnail}" alt="${product.name}" loading="lazy" onerror="this.hidden=true">` : ""}
    <span class="product-badge">${product.brand}</span>
  </div>`;
}

function renderProducts() {
  const products = visibleProducts();
  $("#catalogCount").textContent = `${products.length} product${products.length === 1 ? "" : "s"}`;
  $("#productGrid").innerHTML = products.length ? products.map((product) => `
    <article class="product-card">
      <div class="product-media">
        ${productVisual(product)}
        <button class="quick-add" data-add="${product.id}" type="button"
          aria-label="Add ${product.name} to cart" title="Add to cart"
          ${product.stock_quantity === 0 ? "disabled" : ""}>
          <i data-lucide="${product.stock_quantity === 0 ? "ban" : "plus"}"></i>
        </button>
      </div>
      <div class="product-info">
        <button class="product-name" data-product="${product.id}" type="button">${product.name}</button>
        <span class="product-price">${money(product.price, product.currency)}</span>
        <span class="product-category">${product.category.replaceAll("-", " ")}</span>
        <span class="product-stock">${product.stock_quantity > 0 ? `${product.stock_quantity} available` : "Sold out"}</span>
        <span class="product-rating"><i data-lucide="star"></i>${Number(product.rating || 0).toFixed(1)}
          ${Number(product.discount_percentage || 0) > 0 ? `<span class="product-discount">${Math.round(product.discount_percentage)}% off</span>` : ""}
        </span>
      </div>
    </article>
  `).join("") : `<div class="empty-state"><h3>No products found</h3><p>Try another search or category.</p></div>`;
  refreshIcons();
}

function requireAuth() {
  if (state.token) return true;
  openAuth();
  showToast("Sign in to use your cart");
  return false;
}

async function loadCart() {
  if (!state.token) {
    state.cart = { items: [], total_items: 0, total_amount: 0, currency: "INR" };
    renderCart();
    return;
  }
  try {
    state.cart = await api("/cart");
  } catch {
    logout(false);
  }
  renderCart();
}

function renderCart() {
  $("#cartCount").textContent = state.cart.total_items || 0;
  $("#cartTotal").textContent = money(state.cart.total_amount || 0, state.cart.currency);
  $("#checkoutButton").disabled = !state.cart.items.length;
  $("#cartItems").innerHTML = state.cart.items.length ? state.cart.items.map((item) => `
    <div class="cart-row">
      <div class="cart-thumb">${(categoryStyles[state.products.find((p) => p.id === item.product_id)?.category] || ["•"])[0]}</div>
      <div>
        <h3>${item.product_name}</h3>
        <p>${money(item.unit_price)} each</p>
        <div class="quantity-control">
          <button data-quantity="${item.product_id}" data-value="${item.quantity - 1}" type="button" aria-label="Decrease quantity">−</button>
          <span>${item.quantity}</span>
          <button data-quantity="${item.product_id}" data-value="${item.quantity + 1}" type="button" aria-label="Increase quantity">+</button>
        </div>
      </div>
      <div>
        <strong>${money(item.line_total)}</strong>
        <button class="remove-button" data-remove="${item.product_id}" type="button">Remove</button>
      </div>
    </div>
  `).join("") : `<div class="empty-state"><h3>Your bag is empty</h3><p>Add something useful from the collection.</p></div>`;
}

async function addToCart(productId) {
  if (!requireAuth()) return;
  try {
    state.cart = await api("/cart/items", {
      method: "POST",
      body: JSON.stringify({ product_id: productId, quantity: 1 }),
    });
    renderCart();
    showToast("Added to your bag");
  } catch (error) {
    showToast(error.message);
  }
}

async function updateCartItem(productId, quantity) {
  if (quantity < 1) return removeCartItem(productId);
  try {
    state.cart = await api(`/cart/items/${productId}`, {
      method: "PATCH",
      body: JSON.stringify({ quantity }),
    });
    renderCart();
  } catch (error) {
    showToast(error.message);
  }
}

async function removeCartItem(productId) {
  await api(`/cart/items/${productId}`, { method: "DELETE" });
  await loadCart();
}

function openCart() {
  if (!requireAuth()) return;
  $("#cartDrawer").classList.add("open");
  $("#cartDrawer").setAttribute("aria-hidden", "false");
  $("#scrim").classList.add("active");
}

function closeCart() {
  $("#cartDrawer").classList.remove("open");
  $("#cartDrawer").setAttribute("aria-hidden", "true");
  $("#scrim").classList.remove("active");
}

function openAuth() {
  const loggedIn = Boolean(state.user && state.token);
  $("#accountView").style.display = loggedIn ? "block" : "none";
  $("#authView").style.display = loggedIn ? "none" : "block";
  if (loggedIn) {
    $("#accountName").textContent = state.user.full_name;
    $("#accountEmail").textContent = state.user.email;
  }
  $("#authModal").showModal();
}

function setAuthMode(mode) {
  state.authMode = mode;
  document.body.classList.toggle("register-mode", mode === "register");
  $("#authTitle").textContent = mode === "register" ? "Create account" : "Sign in";
  $("#authSubmitButton").textContent = mode === "register" ? "Create account" : "Sign in";
  $("#fullNameInput").required = mode === "register";
  document.querySelectorAll("[data-auth-mode]").forEach((button) =>
    button.classList.toggle("active", button.dataset.authMode === mode));
}

async function submitAuth(event) {
  event.preventDefault();
  const email = $("#emailInput").value;
  const password = $("#passwordInput").value;
  try {
    if (state.authMode === "register") {
      await api("/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password, full_name: $("#fullNameInput").value }),
      });
    }
    const result = await api("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    state.token = result.access_token;
    state.user = result.user;
    localStorage.setItem("cg_token", state.token);
    localStorage.setItem("cg_user", JSON.stringify(state.user));
    $("#authModal").close();
    await loadCart();
    showToast(`Welcome, ${state.user.full_name.split(" ")[0]}`);
  } catch (error) {
    showToast(error.message);
  }
}

function logout(notify = true) {
  state.token = null;
  state.user = null;
  localStorage.removeItem("cg_token");
  localStorage.removeItem("cg_user");
  if ($("#authModal").open) $("#authModal").close();
  loadCart();
  if (notify) showToast("You’re signed out");
}

function openProduct(productId) {
  const product = state.products.find((item) => item.id === productId);
  if (!product) return;
  $("#productModalContent").innerHTML = `
    <div class="product-detail">
      ${productVisual({ ...product, thumbnail: product.images?.[0] || product.thumbnail })}
      <div class="product-detail-copy">
        <p class="eyebrow">${product.category.replaceAll("-", " ")} · ${product.sku}</p>
        <h2>${product.name}</h2>
        <p>${product.description}</p>
        <span class="detail-price">${money(product.price, product.currency)}</span>
        <p class="detail-rating"><i data-lucide="star"></i>${Number(product.rating || 0).toFixed(1)} rating · ${Math.round(product.discount_percentage || 0)}% off</p>
        <p>${product.stock_quantity > 0 ? `${product.stock_quantity} currently available` : "Currently sold out"}</p>
        <button class="primary-button" data-modal-add="${product.id}" type="button" ${product.stock_quantity === 0 ? "disabled" : ""}>
          Add to bag <i data-lucide="shopping-bag"></i>
        </button>
      </div>
    </div>`;
  $("#productModal").showModal();
  refreshIcons();
}

async function checkout() {
  try {
    const order = await api("/cart/checkout", { method: "POST" });
    closeCart();
    await loadCart();
    await loadProducts();
    $("#successMessage").textContent = `${order.order_number} · ${money(order.total_amount, order.currency)}`;
    $("#successModal").showModal();
  } catch (error) {
    showToast(error.message);
  }
}

document.addEventListener("click", (event) => {
  const target = event.target.closest("button");
  if (!target) return;
  if (target.dataset.category) { state.category = target.dataset.category; renderCategories(); renderProducts(); }
  if (target.dataset.navCategory) {
    state.category = target.dataset.navCategory;
    renderCategories();
    renderProducts();
    $("#catalog").scrollIntoView({ behavior: "smooth", block: "start" });
  }
  if (target.dataset.add) addToCart(Number(target.dataset.add));
  if (target.dataset.product) openProduct(Number(target.dataset.product));
  if (target.dataset.modalAdd) { addToCart(Number(target.dataset.modalAdd)); $("#productModal").close(); }
  if (target.dataset.quantity) updateCartItem(Number(target.dataset.quantity), Number(target.dataset.value));
  if (target.dataset.remove) removeCartItem(Number(target.dataset.remove));
  if (target.dataset.authMode) setAuthMode(target.dataset.authMode);
  if (target.hasAttribute("data-close-modal")) target.closest("dialog").close();
});

$("#searchInput").addEventListener("input", (event) => { state.search = event.target.value; renderProducts(); });
$("#sortSelect").addEventListener("change", (event) => { state.sort = event.target.value; renderProducts(); });
$("#cartButton").addEventListener("click", openCart);
$("#closeCartButton").addEventListener("click", closeCart);
$("#scrim").addEventListener("click", closeCart);
$("#accountButton").addEventListener("click", openAuth);
$("#authForm").addEventListener("submit", submitAuth);
$("#logoutButton").addEventListener("click", () => logout());
$("#checkoutButton").addEventListener("click", checkout);

Promise.all([loadProducts(), loadCart()])
  .catch((error) => showToast(error.message))
  .finally(refreshIcons);
