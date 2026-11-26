// Chat do Assistente do cliente: envia a pergunta e mostra a resposta e como a IA decidiu.
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("chat-form");
  if (!form) return;
  const input = document.getElementById("chat-input");
  const lista = document.getElementById("chat-msgs");
  const csrf = form.querySelector("[name=csrfmiddlewaretoken]").value;

  // Cria um elemento com texto seguro (nunca usa innerHTML com dados do usuário)
  const el = (tag, cls, texto) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (texto !== undefined) e.textContent = texto;
    return e;
  };
  const rolar = () => { lista.scrollTop = lista.scrollHeight; };
  const pct = (v) => `${Math.round(v * 100)}%`;

  // Bloco "Como a IA decidiu": intenção, confiança, alternativas, palavras e ferramenta
  function decisao(r) {
    const d = el("details", "decisao");
    d.append(el("summary", "", `▸ Como a IA decidiu · ${r.nome_intencao} (${pct(r.confianca)})`));
    const dl = el("dl");
    const linha = (rotulo, conteudo) => { dl.append(el("dt", "", rotulo)); const dd = el("dd"); dd.append(conteudo); dl.append(dd); };
    const barras = el("div");
    r.alternativas.forEach((a) => {
      const b = el("div", "barra"); const i = el("i"); i.style.width = `${Math.max(4, a.confianca * 120)}px`;
      b.append(i, el("span", "", `${a.nome} ${pct(a.confianca)}`)); barras.append(b);
    });
    const lim = el("div", "barra limiar"); const li = el("i"); li.style.width = `${r.limiar * 120}px`;
    lim.append(li, el("span", "", `limiar mínimo ${pct(r.limiar)}`)); barras.append(lim);
    linha("Intenções", barras);
    const palavras = el("div", "palavras");
    if (r.palavras.length) r.palavras.forEach((p) => palavras.append(el("span", "", p.palavra)));
    else palavras.append(el("span", "", "—"));
    linha("Palavras-chave", palavras);
    linha("Ferramenta", el("span", "mono", r.ferramenta ? `${r.ferramenta}()` : "nenhuma — confiança abaixo do limiar"));
    d.append(dl);
    return d;
  }

  async function enviar(pergunta) {
    lista.append(el("div", "msg cliente", pergunta));
    const espera = el("div", "digitando", "Assistente consultando os registros…");
    lista.append(espera); rolar();
    try {
      const resp = await fetch(form.dataset.url, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
        body: JSON.stringify({ pergunta }),
      });
      const r = await resp.json();
      espera.remove();
      if (!resp.ok) { lista.append(el("div", "msg bot incerto", r.erro || "Não foi possível responder agora.")); rolar(); return; }
      const msg = el("div", `msg bot${r.respondeu ? "" : " incerto"}`, r.resposta);
      if (r.fonte && r.fonte !== "—") msg.append(el("span", "fonte", `Fonte: ${r.fonte}`));
      msg.append(decisao(r));
      lista.append(msg);
    } catch (e) {
      espera.remove();
      lista.append(el("div", "msg bot incerto", "Sem conexão com a oficina. Tente novamente."));
    }
    rolar();
  }

  form.addEventListener("submit", (ev) => {
    ev.preventDefault();
    const pergunta = input.value.trim();
    if (!pergunta) return;
    input.value = "";
    enviar(pergunta);
  });
  document.querySelectorAll(".chip").forEach((c) => c.addEventListener("click", () => enviar(c.textContent)));
});

// Botão "Copiar" do painel da ordem (lado da oficina)
document.addEventListener("click", (ev) => {
  const botao = ev.target.closest("[data-copiar]");
  if (!botao) return;
  const campo = document.querySelector(botao.dataset.copiar);
  campo.select();
  navigator.clipboard?.writeText(campo.value);
  botao.textContent = "Copiado";
  setTimeout(() => { botao.textContent = "Copiar"; }, 1500);
});
