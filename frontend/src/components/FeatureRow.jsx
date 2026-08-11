import FeatureCard from './FeatureCard';
import './FeatureRow.css';

function FeatureRow({ title, features, onCardClick }) {
  return (
    <div className="feature-row">
      <div className="row-heading">
        <h2 className="row-title">{title}</h2>
      </div>
      <div className="row-container">
        <div className="cards-container">
          {features.map((feature) => (
            <FeatureCard
              key={feature.id}
              feature={feature}
              onClick={() => onCardClick(feature)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default FeatureRow;
