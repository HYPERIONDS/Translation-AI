import './Hero.css';

function Hero() {
  const scrollToFeatures = () => {
    const element = document.getElementById('features');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section id="hero" className="hero-section">
      <div className="hero-content">
        <div className="hero-kicker">Multilingual content tools</div>
        <h1 className="hero-title">Create content for every language.</h1>
        <p className="hero-subtitle">
          Translate text, dub videos, transcribe audio, and produce spoken content from one workspace.
        </p>
        <div className="hero-actions">
          <button className="btn-hero" onClick={scrollToFeatures}>View tools</button>
          <button className="btn-hero-secondary" onClick={() => document.getElementById('faq')?.scrollIntoView({ behavior: 'smooth' })}>Learn more</button>
        </div>
        <p className="hero-note">Video · Audio · Text</p>
      </div>
    </section>
  );
}

export default Hero;
