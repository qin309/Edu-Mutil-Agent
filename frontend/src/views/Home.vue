<template>
  <div class="home-container">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          EduAgent
          <span class="hero-subtitle">Multimodal Educational Assistant</span>
        </h1>
        <p class="hero-description">
          Revolutionize your learning experience with AI-powered multimodal analysis.
          Upload assignments, get instant feedback with knowledge correlations, and accelerate your academic growth.
        </p>

        <div class="hero-features">
          <div class="feature-item">
            <Scan class="feature-icon" />
            <span>Document Correction</span>
          </div>
          <div class="feature-item">
            <Brain class="feature-icon" />
            <span>AI Analysis</span>
          </div>
          <div class="feature-item">
            <BookOpen class="feature-icon" />
            <span>Knowledge Base</span>
          </div>
          <div class="feature-item">
            <TrendingUp class="feature-icon" />
            <span>Progress Tracking</span>
          </div>
        </div>

        <div class="hero-actions">
          <router-link to="/register" class="btn-primary hero-btn">
            Get Started
          </router-link>
          <router-link to="/login" class="hero-link">
            Already have an account?
          </router-link>
        </div>
      </div>

      <div class="hero-visual">
        <div class="visual-card card">
          <div class="upload-preview">
            <FileText class="upload-icon" />
            <p>Drop your assignment here</p>
            <div class="processing-indicator">
              <div class="processing-step active">
                <span class="step-icon">📷</span>
                <span>Document Scanning</span>
              </div>
              <div class="processing-step active">
                <span class="step-icon">🤖</span>
                <span>AI Analysis</span>
              </div>
              <div class="processing-step">
                <span class="step-icon">📚</span>
                <span>Knowledge Correlation</span>
              </div>
              <div class="processing-step">
                <span class="step-icon">📊</span>
                <span>Progress Insights</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <div class="section-container">
        <h2 class="section-title">How It Works</h2>

        <div class="features-grid">
          <div class="feature-card card">
            <div class="feature-number">1</div>
            <h3>Upload Assignment</h3>
            <p>Simply upload photos of your homework, tests, or assignments. Our system handles various formats and automatically corrects any skew or distortion.</p>
            <Upload class="feature-card-icon" />
          </div>

          <div class="feature-card card">
            <div class="feature-number">2</div>
            <h3>AI Analysis</h3>
            <p>Leveraging advanced AI models, we provide detailed analysis of your work, identifying strengths, areas for improvement, and specific knowledge gaps.</p>
            <Brain class="feature-card-icon" />
          </div>

          <div class="feature-card card">
            <div class="feature-number">3</div>
            <h3>Knowledge Correlation</h3>
            <p>Connect your assignments to broader course concepts. See how specific problems relate to your overall learning journey and course objectives.</p>
            <Network class="feature-card-icon" />
          </div>

          <div class="feature-card card">
            <div class="feature-number">4</div>
            <h3>Track Progress</h3>
            <p>Monitor your academic growth over time with comprehensive analytics, personalized recommendations, and targeted study plans.</p>
            <BarChart3 class="feature-card-icon" />
          </div>
        </div>
      </div>
    </section>

    <!-- Demo Section -->
    <section class="demo-section">
      <div class="section-container">
        <div class="demo-content">
          <h2 class="section-title">See EduAgent in Action</h2>
          <div class="demo-grid">
            <div class="demo-item card">
              <div class="demo-header">
                <h4>Mathematics Problem Analysis</h4>
                <span class="demo-subject">Algebra</span>
              </div>
              <div class="demo-result">
                <div class="result-score">
                  <span class="score-label">Solution Quality:</span>
                  <span class="score-value">8.5/10</span>
                </div>
                <div class="result-highlights">
                  <div class="highlight positive">
                    ✓ Correct approach to solving equations
                  </div>
                  <div class="highlight neutral">
                    • Consider alternative solution methods
                  </div>
                  <div class="highlight negative">
                    ✗ Missing step-by-step justification
                  </div>
                </div>
              </div>
            </div>

            <div class="demo-item card">
              <div class="demo-header">
                <h4>Knowledge Gap Analysis</h4>
                <span class="demo-subject">Linear Equations</span>
              </div>
              <div class="demo-result">
                <div class="knowledge-connections">
                  <div class="connection-item">
                    <span class="connection-label">Related Topics:</span>
                    <div class="topics">
                      <span class="topic-tag">Slope-Intercept Form</span>
                      <span class="topic-tag">System of Equations</span>
                      <span class="topic-tag">Graphing Lines</span>
                    </div>
                  </div>
                  <div class="recommendation">
                    <Target class="rec-icon" />
                    <span>Focus on understanding variable relationships</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="demo-item card">
              <div class="demo-header">
                <h4>Progress Tracking</h4>
                <span class="demo-subject">Overall Course</span>
              </div>
              <div class="demo-result">
                <div class="progress-summary">
                  <div class="progress-metric">
                    <span class="metric-label">Average Score:</span>
                    <span class="metric-value">7.8/10</span>
                  </div>
                  <div class="progress-trend">
                    <TrendingUp class="trend-icon positive" />
                    <span>+12% improvement this month</span>
                  </div>
                  <div class="next-steps">
                    <Lightbulb class="step-icon" />
                    <span>Recommended: Practice word problems</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="cta-content">
        <h2>Ready to Transform Your Learning?</h2>
        <p>Join thousands of students who are already using EduAgent to accelerate their academic success.</p>
        <div class="cta-actions">
          <router-link to="/register" class="btn-primary cta-btn">
            Start Learning Smarter
          </router-link>
          <router-link to="/login" class="cta-secondary">
            Sign in to Continue
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import {
  Scan,
  Brain,
  BookOpen,
  TrendingUp,
  FileText,
  Upload,
  Network,
  BarChart3,
  Target,
  Lightbulb
} from 'lucide-vue-next'
</script>

<style scoped>
.home-container {
  width: 100%;
}

/* Hero Section */
.hero-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
  padding: 4rem 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.hero-content {
  z-index: 2;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #10B981 0%, #3B82F6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  display: block;
  font-size: 1.5rem;
  font-weight: 300;
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

.hero-description {
  font-size: 1.1rem;
  line-height: 1.6;
  color: var(--text-secondary);
  margin-bottom: 2rem;
  max-width: 600px;
}

.hero-features {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  margin-bottom: 3rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--text-primary);
  font-weight: 500;
}

.feature-icon {
  width: 1.5rem;
  height: 1.5rem;
  color: var(--primary-color);
}

.hero-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.hero-btn {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
}

.hero-link {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  padding: 1rem;
  transition: color 0.2s;
}

.hero-link:hover {
  color: var(--primary-hover);
}

.hero-visual {
  position: relative;
}

.visual-card {
  position: relative;
  overflow: hidden;
}

.upload-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(59, 130, 246, 0.1));
  border-radius: var(--radius-lg);
  margin: -1.5rem;
}

.upload-icon {
  width: 3rem;
  height: 3rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.processing-indicator {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 2rem;
  width: 100%;
}

.processing-step {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: var(--radius-md);
  background: rgba(15, 23, 42, 0.6);
  transition: all 0.3s;
}

.processing-step.active {
  background: rgba(16, 185, 129, 0.2);
  border-left: 3px solid var(--primary-color);
}

.step-icon {
  font-size: 1.2rem;
}

/* Features Section */
.features-section {
  padding: 6rem 2rem;
  background: rgba(15, 23, 42, 0.3);
}

.section-container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 3rem;
  color: var(--text-primary);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
}

.feature-card {
  text-align: center;
  padding: 2rem;
  position: relative;
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
}

.feature-number {
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #10B981, #3B82F6);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.2rem;
}

.feature-card h3 {
  margin-bottom: 1rem;
  font-size: 1.25rem;
  font-weight: 600;
}

.feature-card p {
  color: var(--text-secondary);
  line-height: 1.6;
}

.feature-card-icon {
  width: 2rem;
  height: 2rem;
  color: var(--primary-color);
  margin-top: 1rem;
}

/* Demo Section */
.demo-section {
  padding: 6rem 2rem;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(16, 185, 129, 0.05));
}

.demo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.demo-item {
  padding: 1.5rem;
}

.demo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.demo-header h4 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.demo-subject {
  background: var(--primary-color);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-md);
  font-size: 0.8rem;
  font-weight: 500;
}

/* CTA Section */
.cta-section {
  padding: 6rem 2rem;
  background: linear-gradient(135deg, #10B981, #3B82F6);
  text-align: center;
}

.cta-content h2 {
  color: white;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.cta-content p {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
  margin-bottom: 2rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.cta-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  align-items: center;
}

.cta-btn {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  background: white;
  color: var(--primary-color);
}

.cta-secondary {
  color: white;
  text-decoration: none;
  font-weight: 500;
  padding: 1rem;
}

.cta-secondary:hover {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: underline;
}

@media (max-width: 1024px) {
  .hero-section {
    grid-template-columns: 1fr;
    gap: 3rem;
  }

  .hero-title {
    font-size: 2.5rem;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 2rem 1rem;
  }

  .hero-title {
    font-size: 2rem;
  }

  .hero-features {
    gap: 1rem;
  }

  .hero-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .features-grid, .demo-grid {
    grid-template-columns: 1fr;
  }

  .section-title {
    font-size: 2rem;
  }

  .cta-actions {
    flex-direction: column;
  }
}
</style>