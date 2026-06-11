const opinionsData = [
  {
    author: "Marek Nowak",
    role: "CTO · TechStartup Gdańsk",
    content: "Jan dostarczył MVP w 10 dni. Kod czysty, dokumentacja kompletna. Wrócimy do niego przy kolejnym projekcie bez zastanowienia.",
    rating: 5
  },
  {
    author: "Anna Wiśniewska",
    role: "Founder · E-commerce Brand",
    content: "Profesjonalizm na każdym kroku — od estymacji, przez komunikację, po deployment. Lighthouse 98/100 na starcie. Polecam wszystkim.",
    rating: 5
  },
  {
    author: "Karolina Brzezińska",
    role: "Product Manager · SaaS Co.",
    content: "Pracowałam z wieloma developerami — Jan wyróżnia się tym, że myśli o produkcie, nie tylko o ticketach. Rare skill.",
    rating: 5
  }
];

const OpinionsSlider = {
  current: 0,
  container: null,

  init() {
    this.render();
    this.startAutoSlide();
  },

  render() {
    this.container.innerHTML = `
      <div class="opinions-slider">
        <button class="opinions-nav prev" onclick="OpinionsSlider.prev()">&laquo;</button>
        <div class="opinions-track">
          ${this.renderSlides()}
        </div>
        <button class="opinions-nav next" onclick="OpinionsSlider.next()">&raquo;</button>
      </div>
      <div class="opinions-dots">
        ${this.renderDots()}
      </div>
    `;
  },

  renderSlides() {
    return opinionsData.map((op, i) => `
      <div class="opinions-slide ${i === 0 ? 'active' : ''}" data-index="${i}">
        <div class="opinions-card">
          <div class="opinions-rating">${'★'.repeat(op.rating)}</div>
          <p class="opinions-content">${op.content}</p>
          <div class="opinions-author">
            <div class="opinions-avatar">${op.author.charAt(0)}</div>
            <div>
              <div class="opinions-name">${op.author}</div>
              <div class="opinions-role">${op.role}</div>
            </div>
          </div>
        </div>
      </div>
    `).join('');
  },

  renderDots() {
    return opinionsData.map((_, i) => `<button class="opinions-dot ${i === 0 ? 'active' : ''}" onclick="OpinionsSlider.goTo(${i})"></button>`).join('');
  },

  goTo(index) {
    const slides = this.container.querySelectorAll('.opinions-slide');
    const dots = this.container.querySelectorAll('.opinions-dot');
    
    slides.forEach(s => s.classList.remove('active'));
    dots.forEach(d => d.classList.remove('active'));
    
    this.current = (index + opinionsData.length) % opinionsData.length;
    slides[this.current].classList.add('active');
    dots[this.current].classList.add('active');
  },

  next() {
    this.goTo(this.current + 1);
  },

  prev() {
    this.goTo(this.current - 1);
  },

  startAutoSlide() {
    setInterval(() => this.next(), 5000);
  }
};

document.addEventListener('DOMContentLoaded', () => {
  OpinionsSlider.container = document.getElementById('opinions-container');
  OpinionsSlider.init();
});