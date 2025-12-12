import { useState, useEffect } from "react";
import "./index.css";

const API_URL = "http://127.0.0.1:5000";

function App() {
  const [recipes, setRecipes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    cook_time: "",
    difficulty: "",
    category_id: "",
  });
  const [editingId, setEditingId] = useState(null);

  const [filterData, setFilterData] = useState({
    category: "",
    difficulty: "",
    max_time: "",
  });
  const [reportData, setReportData] = useState([]);

  useEffect(() => {
    fetchRecipes();
    fetchCategories();
  }, []);

  const fetchRecipes = async () => {
    const res = await fetch(`${API_URL}/api/recipes`);
    setRecipes(await res.json());
  };

  const fetchCategories = async () => {
    const res = await fetch(`${API_URL}/api/categories`);
    setCategories(await res.json());
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    const url = editingId
      ? `${API_URL}/api/recipes/${editingId}`
      : `${API_URL}/api/recipes`;
    const method = editingId ? "PUT" : "POST";

    await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...formData,
        cook_time: Number(formData.cook_time) || null,
        category_id: Number(formData.category_id) || null,
      }),
    });

    setFormData({
      title: "",
      description: "",
      cook_time: "",
      difficulty: "",
      category_id: "",
    });
    setEditingId(null);
    fetchRecipes();
  };

  const handleEdit = (r) => {
    setEditingId(r.id);
    setFormData({
      title: r.title,
      description: r.description || "",
      cook_time: r.cook_time || "",
      difficulty: r.difficulty || "",
      category_id: r.category_id || "",
    });
  };

  const handleDelete = async (id) => {
    if (window.confirm("Delete this recipe?")) {
      await fetch(`${API_URL}/api/recipes/${id}`, { method: "DELETE" });
      fetchRecipes();
    }
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilterData((prev) => ({ ...prev, [name]: value }));
  };

  const handleReportSubmit = async (e) => {
    e.preventDefault();
    const params = new URLSearchParams();
    Object.entries(filterData).forEach(([k, v]) => v && params.append(k, v));
    const res = await fetch(`${API_URL}/api/report?${params.toString()}`);
    setReportData(await res.json());
  };

  return (
    <div className="wrapper">
      <header>
        <h1>Recipe Organizer</h1>
        <p>Manage and explore your favorite recipes</p>
      </header>

      <main>
        {}
        <section className="card">
          <h2>{editingId ? "Edit Recipe" : "Add New Recipe"}</h2>
          <form className="grid" onSubmit={handleFormSubmit}>
            <input
              name="title"
              value={formData.title}
              onChange={handleFormChange}
              placeholder="Recipe title"
              required
            />
            <textarea
              name="description"
              value={formData.description}
              onChange={handleFormChange}
              placeholder="Description"
              rows="3"
            />
            <input
              type="number"
              name="cook_time"
              value={formData.cook_time}
              onChange={handleFormChange}
              placeholder="Cook time (minutes)"
            />
            <select
              name="difficulty"
              value={formData.difficulty}
              onChange={handleFormChange}
            >
              <option value="">Select difficulty</option>
              <option>Easy</option>
              <option>Medium</option>
              <option>Hard</option>
            </select>
            <select
              name="category_id"
              value={formData.category_id}
              onChange={handleFormChange}
            >
              <option value="">Select category</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>

            <div className="form-actions">
              <button type="submit">
                {editingId ? "Update Recipe" : "Add Recipe"}
              </button>
              {editingId && (
                <button
                  type="button"
                  className="secondary"
                  onClick={() => setEditingId(null)}
                >
                  Cancel
                </button>
              )}
            </div>
          </form>
        </section>

        {/* --- Recipe List --- */}
        <section className="card">
          <h2>All Recipes</h2>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Category</th>
                  <th>Difficulty</th>
                  <th>Time</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {recipes.map((r) => (
                  <tr key={r.id}>
                    <td>{r.title}</td>
                    <td>{r.category_name || "—"}</td>
                    <td>{r.difficulty}</td>
                    <td>{r.cook_time} min</td>
                    <td>
                      <button onClick={() => handleEdit(r)}>✏️</button>
                      <button onClick={() => handleDelete(r.id)}>🗑️</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {}
        <section className="card">
          <h2>Recipe Report</h2>
          <form className="filter-grid" onSubmit={handleReportSubmit}>
            <select
              name="category"
              value={filterData.category}
              onChange={handleFilterChange}
            >
              <option value="">All categories</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>

            <select
              name="difficulty"
              value={filterData.difficulty}
              onChange={handleFilterChange}
            >
              <option value="">All difficulties</option>
              <option>Easy</option>
              <option>Medium</option>
              <option>Hard</option>
            </select>

            <input
              type="number"
              name="max_time"
              value={filterData.max_time}
              onChange={handleFilterChange}
              placeholder="Max cook time"
            />

            <button type="submit">Generate</button>
          </form>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Category</th>
                  <th>Difficulty</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {reportData.length > 0 ? (
                  reportData.map((r) => (
                    <tr key={r.id}>
                      <td>{r.title}</td>
                      <td>{r.category_name || "—"}</td>
                      <td>{r.difficulty}</td>
                      <td>{r.cook_time} min</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="4" style={{ textAlign: "center" }}>
                      No results yet — try filtering.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
