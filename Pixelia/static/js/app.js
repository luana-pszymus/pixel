function toggleAjustes() {
  const s = document.getElementById("secao-ajustes");

  s.style.display = s.style.display === "block" ? "none" : "block";
}

// =====================================================
// ENTER SOCOR
// =====================================================

const textarea = document.getElementById("pergunta");

textarea.addEventListener("keydown", function (event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();

    gerar();
  }
});

// =====================================================
// GERAR
// =====================================================

async function gerar() {
  const box = document.getElementById("resultado");

  const pergunta = document.getElementById("pergunta").value;

  const btn = document.querySelector(".btn-gerar");

  if (!pergunta) {
    alert("Dê uma ideia para a Polímnia!");

    return;
  }

  btn.disabled = true;

  btn.innerText = "GERANDO...";

  box.style.display = "block";

  box.classList.add("loading");

  const mensagens = [
    "Analisando paleta...",
    "Criando direção artística...",
    "Definindo iluminação...",
    "Refinando consistência visual...",
  ];

  let i = 0;

  box.innerText = mensagens[i];

  const interval = setInterval(() => {
    i = (i + 1) % mensagens.length;

    box.innerText = mensagens[i];
  }, 1500);

  try {
    const res = await fetch("/perguntar", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        pergunta: pergunta,

        tamanho: document.getElementById("tamanho").value,

        paleta: document.getElementById("paleta").value,

        significado: document.getElementById("significado").value,

        modo: document.getElementById("modo").value,
      }),
    });

    const data = await res.json();

    clearInterval(interval);

    box.classList.remove("loading");

    box.innerText = data.resposta || "Erro ao gerar.";

    carregarPaletas();

    document.getElementById("pergunta").value = "";

    btn.disabled = false;

    btn.innerText = "CRIAR DIREÇÃO ARTÍSTICA";
  } catch (e) {
    clearInterval(interval);

    box.classList.remove("loading");

    box.innerText = "Erro na conexão.";

    btn.disabled = false;

    btn.innerText = "CRIAR DIREÇÃO ARTÍSTICA";
  }
}

// =====================================================
// CARREGAR PALETAS
// =====================================================

async function carregarPaletas() {
  try {
    const res = await fetch("/paletas");

    const paletas = await res.json();

    const lista = document.getElementById("lista-paletas");

    lista.innerHTML = "";

    paletas.forEach((p) => {
      const card = document.createElement("div");

      card.className = "paleta-card";

      let coresHTML = "";

      const stringCores = p.cores.replace(/\n/g, ",").replace(/\s/g, "");

      const cores = stringCores.split(",");

      cores.forEach((cor) => {
        if (cor.trim() !== "") {
          coresHTML += `
            <div
              class="cor"
              style="background: ${cor.trim()};"
              title="${cor.trim()}"
            ></div>
          `;
        }
      });

      card.innerHTML = `
        <strong>${p.nome}</strong>

        <div style="margin-top:8px;font-size:13px;">
          ${p.significados || ""}
        </div>

        <div class="paleta-cores">
          ${coresHTML}
        </div>

        <div style="display:flex; gap:5px; margin-top:10px;">

        <button
          class="btn-usar"
          onclick="usarPaleta('${p.cores.replace(/\n/g, "\\n")}', '${p.significados || ""}')"
        >
          Usar
        </button>

        <button
          class="btn-deletar"
          onclick="deletarPaleta(${p.id})"
        >
          🗑️
        </button>

      </div>

        <button
          class="btn-editar"
          onclick="editarPaleta(
            ${p.id},
            \`${p.nome}\`,
            \`${p.cores}\`,
            \`${p.significados || ""}\`
          )"
        >
          ✏️ Editar
        </button>
      `;
      lista.appendChild(card);
    });
  } catch (e) {
    console.log(e);
  }
}

// =====================================================
// USAR PALETA
// =====================================================

function usarPaleta(cores, significados) {
  document.getElementById("paleta").value = cores;

  document.getElementById("significado").value = significados;
}

async function editarPaleta(id, nomeAtual, coresAtual, significadoAtual) {
  const novoNome = prompt("Nome da paleta:", nomeAtual);

  if (novoNome === null) return;

  const novasCores = prompt("Cores HEX:", coresAtual);

  if (novasCores === null) return;

  const novoSignificado = prompt("Significados:", significadoAtual);

  if (novoSignificado === null) return;

  try {
    const res = await fetch(`/editar_paleta/${id}`, {
      method: "PUT",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        nome: novoNome,
        cores: novasCores,
        significados: novoSignificado,
      }),
    });

    const data = await res.json();

    alert(data.mensagem);

    carregarPaletas();
  } catch (e) {
    console.error(e);

    alert("Erro ao editar paleta.");
  }
}

async function deletarPaleta(id) {
  const confirmar = confirm("Deseja realmente apagar esta paleta?");

  if (!confirmar) return;

  try {
    await fetch(`/deletar_paleta/${id}`, {
      method: "DELETE",
    });

    carregarPaletas();
  } catch (e) {
    alert("Erro ao apagar paleta.");
  }
}

// =====================================================
// INICIAR
// =====================================================

carregarPaletas();
