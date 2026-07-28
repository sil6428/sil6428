import { mkdir, writeFile } from "node:fs/promises";

const owner = process.env.PROFILE_OWNER || "sil6428";
const token = process.env.GH_STATS_TOKEN;

function escapeXml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");
}

async function github(path) {
  const headers = {
    Accept: "application/vnd.github+json",
    "User-Agent": `${owner}-profile-stats`,
    "X-GitHub-Api-Version": "2022-11-28",
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`https://api.github.com${path}`, { headers });
  if (!response.ok) {
    throw new Error(`GitHub API request failed (${response.status}) for ${path}`);
  }
  return response.json();
}

const [profile, commits] = await Promise.all([
  github(`/users/${encodeURIComponent(owner)}`),
  github(`/search/commits?q=${encodeURIComponent(`author:${owner}`)}&per_page=1`),
]);

let repositoryCount = profile.public_repos;
let privateAccess = false;

if (token) {
  try {
    const viewer = await github("/user");
    if (viewer.login?.toLowerCase() === owner.toLowerCase()) {
      const repositories = await github("/user/repos?affiliation=owner&visibility=all&per_page=100");
      repositoryCount = repositories.length;
      privateAccess = true;
    }
  } catch {
    // A repository-scoped GITHUB_TOKEN still produces an accurate public card.
  }
}

const totalCommits = commits.total_count;
const subtitle = privateAccess
  ? "public + private repositories"
  : "public repositories";
const formatter = new Intl.NumberFormat("en-CA");

const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="495" height="195" viewBox="0 0 495 195" role="img" aria-labelledby="title description">
  <title id="title">${escapeXml(owner)} GitHub activity</title>
  <desc id="description">All-time GitHub commit and repository totals.</desc>
  <defs>
    <linearGradient id="background" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#1a1b27"/>
      <stop offset="1" stop-color="#111827"/>
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="493" height="193" rx="10" fill="url(#background)" stroke="#30363d"/>
  <text x="28" y="37" fill="#70a5fd" font-family="Segoe UI,Ubuntu,sans-serif" font-size="18" font-weight="700">All-time GitHub activity</text>
  <text x="28" y="59" fill="#737aa2" font-family="Segoe UI,Ubuntu,sans-serif" font-size="11">${escapeXml(subtitle)}</text>
  <g font-family="Segoe UI,Ubuntu,sans-serif">
    <text x="28" y="103" fill="#38bdae" font-size="13">Total commits</text>
    <text x="28" y="137" fill="#bf91f3" font-size="28" font-weight="700">${formatter.format(totalCommits)}</text>
    <text x="225" y="103" fill="#38bdae" font-size="13">Repositories</text>
    <text x="225" y="137" fill="#bf91f3" font-size="28" font-weight="700">${formatter.format(repositoryCount)}</text>
    <text x="385" y="103" fill="#38bdae" font-size="13">Followers</text>
    <text x="385" y="137" fill="#bf91f3" font-size="28" font-weight="700">${formatter.format(profile.followers)}</text>
  </g>
  <text x="28" y="173" fill="#737aa2" font-family="Segoe UI,Ubuntu,sans-serif" font-size="10">Generated from GitHub data. Refreshed daily when totals change.</text>
</svg>
`;

await mkdir("profile", { recursive: true });
await writeFile("profile/stats.svg", svg, "utf8");
