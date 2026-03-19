document.addEventListener("DOMContentLoaded", () => {
  renderStatusPage();
});

async function renderStatusPage() {
  try {
    const [originalCards, currentCards] = await Promise.all([
      fetchJson("chara_org.json"),
      fetchJson("chara.json"),
    ]);
    const { unchanged, updated } = buildLists(originalCards, currentCards);
    renderList("unchangedList", unchanged);
    renderList("updatedList", updated);
  } catch (error) {
    document.getElementById("errorMessage").hidden = false;
  }
}

async function fetchJson(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`${path} の取得に失敗しました`);
  }
  return response.json();
}

function buildLists(originalCards, currentCards) {
  const originalMap = new Map(originalCards.map((card) => [card.name, card]));
  const unchanged = [];
  const updated = [];

  currentCards.forEach((currentCard) => {
    if (currentCard.rare !== "SSR") {
      return;
    }

    const originalCard = originalMap.get(currentCard.name);
    if (!originalCard) {
      return;
    }

    const name = buildCardName(currentCard);
    const entry = {
      name,
      wikiURL: currentCard.wikiURL || "",
    };
    if (isUpdated(originalCard, currentCard)) {
      updated.push(entry);
      return;
    }

    unchanged.push(entry);
  });

  return { unchanged, updated };
}

function buildCardName(card) {
  if (card.chara && card.costume) {
    return `${card.chara}【${card.costume}】`;
  }
  return card.chara || card.name;
}

function isUpdated(originalCard, currentCard) {
  return Number(originalCard.hp) !== Number(currentCard.hp) ||
    Number(originalCard.atk) !== Number(currentCard.atk);
}

function renderList(listId, entries) {
  const list = document.getElementById(listId);
  list.innerHTML = "";
  const fragment = document.createDocumentFragment();
  entries.forEach((entry) => {
    const item = document.createElement("li");
    if (entry.wikiURL) {
      const link = document.createElement("a");
      link.href = entry.wikiURL;
      link.target = "_blank";
      link.rel = "noreferrer";
      link.textContent = entry.name;
      item.appendChild(link);
    } else {
      item.textContent = entry.name;
    }
    fragment.appendChild(item);
  });
  list.appendChild(fragment);
}
