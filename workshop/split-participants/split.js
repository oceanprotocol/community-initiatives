const axios = require("axios");
const fs = require("fs");
const path = require("path");

const jsonUrl = 'https://raw.githubusercontent.com/bogdanfazakas/datasets/refs/heads/main/participants.json';
const outputPath = "/data/outputs/grouped_users.json";

const GROUPS = ["image-processing", "real-estate", "rug-pull-analyser"];

async function fetchAndGroupJSON(url) {
  try {
    const response = await axios.get(url);
    const users = response.data;

    if (!Array.isArray(users)) {
      throw new Error("Expected JSON to be an array of user objects.");
    }

    const names = users.map(user => user.name).filter(Boolean);

    const shuffled = names.sort(() => 0.5 - Math.random());

    const grouped = {
      "image-processing": [],
      "real-estate": [],
      "rug-pull-analyser": []
    };

    shuffled.forEach((name, index) => {
      const group = GROUPS[index % GROUPS.length];
      grouped[group].push(name);
    });

    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, JSON.stringify(grouped, null, 2));

    console.log("✅ Grouping complete. Output saved to:", outputPath);
    console.log(grouped);
  } catch (err) {
    console.error("❌ Error:", err.message);
  }
}

fetchAndGroupJSON(jsonUrl);