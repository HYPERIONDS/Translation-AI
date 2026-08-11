import { useState, useEffect } from 'react';
import { useAuth } from '../auth-context';
import LoginModal from './LoginModal';
import SignupModal from './SignupModal';
import './Header.css';

function Header() {
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showSignupModal, setShowSignupModal] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const { user, logout } = useAuth();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <>
      <header className={`site-header ${isScrolled ? 'scrolled' : ''}`}>
        <div className="header-container">
          <div className="header-left">
            <button className="brand" onClick={() => scrollToSection('hero')} aria-label="Bhasha AI home">
              <span className="brand-mark">भ</span>
              <span className="brand-copy">
                <strong>Bhasha AI</strong>
                <small>Language studio</small>
              </span>
            </button>
            <nav className="nav-links">
              <a onClick={() => scrollToSection('hero')}>Home</a>
              <a onClick={() => scrollToSection('features')}>Studio</a>
              <a onClick={() => scrollToSection('faq')}>FAQ</a>
            </nav>
          </div>
          
          <div className="header-right">
            {user ? (
              <>
                <span className="user-name">Hi, {user.name}</span>
                <button className="btn-logout" onClick={logout}>
                  Log Out
                </button>
              </>
            ) : (
              <>
                <button className="btn-login" onClick={() => setShowLoginModal(true)}>
                  Log In
                </button>
                <button className="btn-signup" onClick={() => setShowSignupModal(true)}>
                  Sign Up
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      {showLoginModal && (
        <LoginModal 
          onClose={() => setShowLoginModal(false)} 
          onSwitchToSignup={() => {
            setShowLoginModal(false);
            setShowSignupModal(true);
          }}
        />
      )}
      {showSignupModal && (
        <SignupModal 
          onClose={() => setShowSignupModal(false)} 
          onSwitchToLogin={() => {
            setShowSignupModal(false);
            setShowLoginModal(true);
          }}
        />
      )}
    </>
  );
}

export default Header;
