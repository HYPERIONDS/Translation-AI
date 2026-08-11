import './FeatureCard.css';

function FeatureCard({ feature, onClick }) {
  return (
    <button className="feature-card-netflix" onClick={onClick}>
      <div className="card-image" style={{
        backgroundImage: feature.image ? `url(${feature.image})` : 'none',
        backgroundSize: 'cover',
        backgroundPosition: 'center'
      }}>
        {!feature.image && <span className="card-icon">{feature.icon}</span>}
      </div>
      <div className="card-overlay">
        <h3>{feature.title}</h3>
        <p>{feature.shortDesc}</p>
        <span className="card-link">Open tool <b>→</b></span>
      </div>
    </button>
  );
}

export default FeatureCard;
