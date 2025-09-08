if (!localStorage.getItem('access_token')) {
  window.location.href = '/login';
}
const API_BASE = "api/users";

document.addEventListener("DOMContentLoaded", () => {
  loadUsers();
  document.getElementById("userForm").addEventListener("submit", saveUser);
});

async function loadUsers() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    window.location.href = '/login';
    return;
  }

  const tbody = document.querySelector("#usersTable tbody");
  tbody.innerHTML = `<tr><td colspan="7" class="text-center">Загрузка...</td></tr>`;

  try {
    const res = await fetch(API_BASE, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (res.status === 401) {
      // Токен недействителен
      localStorage.removeItem('access_token');
      window.location.href = '/login';
      return;
    }

    if (!res.ok) {
      throw new Error(`Ошибка: ${res.status}`);
    }

    const users = await res.json();
    tbody.innerHTML = users.map(u => `
      <tr>
        <td>${u.id}</td>
        <td>${u.tg_id}</td>
        <td>${u.first_name ?? ""}</td>
        <td>${u.last_name ?? ""}</td>
        <td>${u.business ?? ""}</td>
        <td>${u.verification_status}</td>
        <td><button class="btn btn-sm btn-neon" onclick="openUser(${u.id})">✏️</button></td>
      </tr>
    `).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-danger">Ошибка: ${err.message}</td></tr>`;
  }
}

async function openUser(id) {
  const res = await fetch(`${API_BASE}/${id}`);
  if (!res.ok) return alert("Ошибка загрузки");
  const u = await res.json();

  document.getElementById("userId").value = u.id;
  document.getElementById("firstName").value = u.first_name ?? "";
  document.getElementById("lastName").value = u.last_name ?? "";
  document.getElementById("patronymic").value = u.patronymic ?? "";
  document.getElementById("business").value = u.business ?? "";
  document.getElementById("verificationStatus").value = u.verification_status;

  new bootstrap.Modal(document.getElementById("userModal")).show();
}

async function saveUser(e) {
  e.preventDefault();
  const id = document.getElementById("userId").value;
  const token = localStorage.getItem('access_token');
  const payload = {
    first_name: document.getElementById("firstName").value,
    last_name: document.getElementById("lastName").value,
    patronymic: document.getElementById("patronymic").value,
    business: document.getElementById("business").value,
    verification_status: document.getElementById("verificationStatus").value,
  };

  const res = await fetch(`${API_BASE}/${id}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify(payload),
  });

  if (res.status === 401) {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
    return;
  }

  if (!res.ok) {
    alert("Ошибка сохранения");
    return;
  }

  new bootstrap.Modal(document.getElementById("userModal")).hide();
  loadUsers();
}
