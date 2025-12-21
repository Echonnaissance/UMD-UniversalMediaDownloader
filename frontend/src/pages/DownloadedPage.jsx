import { useEffect, useState } from "react";
import downloadService from "../services/downloadService";
import "./DownloadedPage.css";

export default function DownloadedPage() {
  const [downloads, setDownloads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    fetchDownloads();
  }, []);

  const fetchDownloads = async () => {
    try {
      const data = await downloadService.getAllDownloads({
        status: "completed",
        limit: 200,
      });
      setDownloads(data || []);
      if (!selected && data && data.length > 0) setSelected(data[0]);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Failed to load downloads");
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <p>Loading downloaded media…</p>;
  if (error) return <p>{error}</p>;

  return (
    <div className="downloaded-page">
      <h2>Downloaded Media</h2>
      {downloads.length === 0 && <p>No completed downloads yet.</p>}

      <div className="downloaded-container">
        <div className="player-column">
          {selected ? (
            <>
              <div className="player-card">
                <h3 className="player-title">
                  {selected.title || selected.file_name}
                </h3>
                <video
                  controls
                  preload="metadata"
                  src={
                    selected.media_url || `/api/downloads/${selected.id}/file`
                  }
                  className="main-player"
                />
              </div>
            </>
          ) : (
            <p>Select a video on the right to play</p>
          )}
        </div>

        <aside className="list-column" aria-label="Downloaded videos">
          {downloads.map((d) => (
            <div
              key={d.id}
              className={`list-item ${
                selected && selected.id === d.id ? "active" : ""
              }`}
              onClick={() => setSelected(d)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === "Enter" && setSelected(d)}
            >
              <img src={d.thumbnail_url} alt={d.title} className="list-thumb" />
              <div className="list-meta">
                <div className="list-title">{d.title || d.file_name}</div>
                <div className="list-sub">
                  {d.duration ? `${Math.round(d.duration)}s` : ""}
                </div>
              </div>
            </div>
          ))}
        </aside>
      </div>
    </div>
  );
}
