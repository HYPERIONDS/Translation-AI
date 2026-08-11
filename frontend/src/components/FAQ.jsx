import { useState } from 'react';
import './FAQ.css';

function FAQ() {
  const [openIndex, setOpenIndex] = useState(null);

  const faqs = [
    {
      question: 'What is Bhasha AI?',
      answer: 'Bhasha AI is a professional AI-powered platform for video dubbing, story generation, article-to-podcast conversion, speech transcription, and text translation. We use advanced AI technology from ElevenLabs and Google Gemini to deliver high-quality, natural-sounding results across 50+ languages.'
    },
    {
      question: 'How does the video dubbing feature work?',
      answer: 'Our video dubbing feature uses AI to extract audio from your video, translate it to your chosen language, generate natural-sounding dubbed audio with the same emotional tone, and synchronize it perfectly with your video. The entire process is automated and typically takes just a few minutes, delivering professional-quality dubbed videos ready for global audiences.'
    },
    {
      question: 'Which languages are supported?',
      answer: 'Bhasha AI supports 50+ languages including English, Spanish, French, German, Hindi, Mandarin, Japanese, Korean, Arabic, Portuguese, Italian, Russian, and many more. Our AI ensures natural translations while preserving context, tone, and cultural nuances.'
    },
    {
      question: 'What file formats are supported?',
      answer: 'For video dubbing, we support common formats like MP4, AVI, MOV, and MKV. Speech transcription accepts common audio formats such as WAV, MP3, and M4A, while generated podcasts and story narration are available as widely compatible audio files.'
    },
    {
      question: 'How accurate is the translation?',
      answer: 'Our translations use Google Gemini AI, which provides highly accurate, context-aware translations. The AI understands idioms, cultural references, and maintains the original meaning while adapting to the target language naturally. For critical content, we recommend reviewing translations, but our accuracy rate is excellent for most use cases.'
    },
    {
      question: 'Is there a limit on video length or file size?',
      answer: 'File size and video length limits depend on your subscription plan. Free users can process videos up to 10 minutes and 100MB. Premium users enjoy extended limits with videos up to 2 hours and 1GB file sizes. Check your account dashboard for specific limits.'
    },
    {
      question: 'Can I use Bhasha AI for commercial purposes?',
      answer: 'Yes! Bhasha AI can be used for commercial projects including marketing videos, educational content, podcasts, YouTube videos, and business presentations. All content you create with our platform is yours to use commercially. Please review our Terms of Service for complete licensing details.'
    },
    {
      question: 'How do I get started?',
      answer: 'Getting started is easy! Sign up for a free account, choose video dubbing, story generation, article-to-podcast, speech-to-text, or translation, provide your content and options, and let the AI do the work. Your processed content will be ready to review or download in minutes.'
    }
  ];

  const toggleFAQ = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section id="faq" className="faq-section">
      <h2 className="faq-title">Frequently Asked Questions</h2>
      <div className="faq-container">
        {faqs.map((faq, index) => (
          <div key={index} className="faq-item">
            <button 
              className={`faq-question ${openIndex === index ? 'active' : ''}`}
              onClick={() => toggleFAQ(index)}
            >
              <span>{faq.question}</span>
              <span className="faq-icon">{openIndex === index ? '×' : '+'}</span>
            </button>
            <div className={`faq-answer ${openIndex === index ? 'open' : ''}`}>
              <p>{faq.answer}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default FAQ;
