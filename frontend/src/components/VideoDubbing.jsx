import { useState } from 'react';
import { api } from '../api';

function VideoDubbing() {
  const [videoFile, setVideoFile] = useState(null);
  const [sourceLang, setSourceLang] = useState('en');
  const [targetLang, setTargetLang] = useState('hi');
  const [loading, setLoading] = useState(false);
  const [dubbingId, setDubbingId] = useState(null);
  const [status, setStatus] = useState('');
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);

  const languages = {
    'en': '🇬🇧 English',
    'hi': '🇮🇳 Hindi',
    'es': '🇪🇸 Spanish',
    'fr': '🇫🇷 French',
    'de': '🇩🇪 German',
    'it': '🇮🇹 Italian',
    'pt': '🇵🇹 Portuguese',
    'ja': '🇯🇵 Japanese',
    'ko': '🇰🇷 Korean',
    'zh': '🇨🇳 Chinese'
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.size > 100 * 1024 * 1024) {
      setError('File too large (max 100MB)');
      return;
    }
    setVideoFile(file);
    setError(null);
    setDubbingId(null);
    setStatus('');
    setProgress(0);
  };

  const checkStatus = async (id) => {
    try {
      const result = await api.getDubbingStatus(id);
      setStatus(result.status);
      
      if (result.status === 'dubbing') {
        setProgress(50);
        setTimeout(() => checkStatus(id), 3000);
      } else if (result.status === 'dubbed') {
        setProgress(100);
        setLoading(false);
      } else if (result.status === 'error' || result.status === 'failed') {
        setError('Dubbing failed. Please try again.');
        setLoading(false);
      }
    } catch {
      setError('Failed to check status');
      setLoading(false);
    }
  };

  const handleDub = async () => {
    if (!videoFile) {
      setError('Please upload a video file first');
      return;
    }

    setLoading(true);
    setError(null);
    setProgress(10);
    setStatus('Starting dubbing...');

    try {
      const result = await api.startVideoDubbing(videoFile, sourceLang, targetLang);
      setDubbingId(result.dubbing_id);
      setProgress(30);
      setStatus('Processing...');
      
      checkStatus(result.dubbing_id);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to start dubbing');
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!dubbingId) return;

    try {
      const blob = await api.downloadDubbedVideo(dubbingId, targetLang);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `dubbed_video_${Date.now()}.mp4`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch {
      setError('Failed to download video');
    }
  };

  return (
    <div className="feature-content">
      <input
        type="file"
        accept=".mp4,.avi,.mov,.mkv"
        onChange={handleFileChange}
        className="file-input"
      />
      {videoFile && (
        <div className="success-message">✅ Uploaded: {videoFile.name}</div>
      )}
      
      {videoFile && (
        <div className="language-selector-duo">
          <div>
            <label>🌍 Source Language</label>
            <select value={sourceLang} onChange={(e) => setSourceLang(e.target.value)}>
              {Object.entries(languages).map(([code, name]) => (
                <option key={code} value={code}>{name}</option>
              ))}
            </select>
          </div>
          <div>
            <label>🎯 Target Language</label>
            <select value={targetLang} onChange={(e) => setTargetLang(e.target.value)}>
              {Object.entries(languages).map(([code, name]) => (
                <option key={code} value={code}>{name}</option>
              ))}
            </select>
          </div>
        </div>
      )}

      <button onClick={handleDub} disabled={loading || !videoFile} className="primary-btn">
        {loading ? 'Processing...' : '🎬 Start Dubbing'}
      </button>

      {loading && (
        <div className="progress-container">
          <div className="progress-bar" style={{ width: `${progress}%` }}></div>
          <div className="status-text">{status}</div>
        </div>
      )}

      {error && <div className="error-message">{error}</div>}

      {status === 'dubbed' && dubbingId && (
        <>
          <div className="success-message">✅ Dubbing completed successfully! 🎉</div>
          <button onClick={handleDownload} className="download-btn">
            📥 Download Dubbed Video
          </button>
        </>
      )}
    </div>
  );
}

export default VideoDubbing;
