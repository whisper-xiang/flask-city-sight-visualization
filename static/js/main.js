// 主要JavaScript功能
document.addEventListener("DOMContentLoaded", function () {
  // 初始化工具提示
  var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // 表单验证增强
  const forms = document.querySelectorAll(".needs-validation");
  Array.from(forms).forEach((form) => {
    form.addEventListener(
      "submit",
      (event) => {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add("was-validated");
      },
      false
    );
  });

  // 导航栏折叠优化
  initNavbarEnhancements();

  // 初始化页面动画效果
  initPageAnimations();

  // 初始化鼠标跟踪效果
  initMouseTracking();

  // 初始化滚动动画
  initScrollAnimations();
});

// 导航栏增强功能
function initNavbarEnhancements() {
  const navbarCollapse = document.getElementById("navbarNav");
  const navbarToggler = document.querySelector(".navbar-toggler");
  const navLinks = document.querySelectorAll(".navbar-nav .nav-link");

  // 点击导航链接后自动关闭折叠菜单（移动端）
  navLinks.forEach((link) => {
    link.addEventListener("click", function () {
      if (window.innerWidth < 992) {
        const collapse = new bootstrap.Collapse(navbarCollapse, {
          toggle: false,
        });
        collapse.hide();
      }
    });
  });

  // 监听折叠菜单的显示/隐藏事件
  navbarCollapse.addEventListener("show.bs.collapse", function () {
    document.body.style.overflow = "hidden"; // 防止背景滚动
  });

  navbarCollapse.addEventListener("hide.bs.collapse", function () {
    document.body.style.overflow = ""; // 恢复滚动
  });

  // 添加滚动时的导航栏效果
  let lastScrollTop = 0;
  const navbar = document.querySelector(".navbar");

  window.addEventListener("scroll", function () {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

    if (scrollTop > lastScrollTop && scrollTop > 100) {
      // 向下滚动时隐藏导航栏
      navbar.style.transform = "translateY(-100%)";
    } else {
      // 向上滚动时显示导航栏
      navbar.style.transform = "translateY(0)";
    }

    lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
  });

  // 为导航栏添加平滑过渡
  navbar.style.transition = "transform 0.3s ease-in-out";

  // 活跃链接高亮
  highlightActiveNavLink();
}

// 高亮当前活跃的导航链接
function highlightActiveNavLink() {
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll(".navbar-nav .nav-link");

  navLinks.forEach((link) => {
    const href = link.getAttribute("href");
    if (href === currentPath || (href === "/" && currentPath === "/index")) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });
}

// 图表初始化函数
function initChart(elementId, option) {
  const chartDom = document.getElementById(elementId);
  if (!chartDom) return null;

  const myChart = echarts.init(chartDom);
  myChart.setOption(option);

  // 响应式调整
  window.addEventListener("resize", function () {
    myChart.resize();
  });

  return myChart;
}

// AJAX请求封装
function apiRequest(url, options = {}) {
  const defaultOptions = {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "X-Requested-With": "XMLHttpRequest",
    },
  };

  const finalOptions = { ...defaultOptions, ...options };

  return fetch(url, finalOptions)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .catch((error) => {
      console.error("API请求失败:", error);
      throw error;
    });
}

// 格式化数字
function formatNumber(num) {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + "万";
  }
  return num.toLocaleString();
}

// 格式化评分
function formatRating(rating) {
  if (!rating) return "暂无评分";
  const stars =
    "★".repeat(Math.floor(rating)) + "☆".repeat(5 - Math.floor(rating));
  return `${stars} ${rating.toFixed(1)}`;
}

// 加载状态管理
function showLoading(elementId) {
  const element = document.getElementById(elementId);
  if (element) {
    element.innerHTML =
      '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">加载中...</span></div></div>';
  }
}

function hideLoading(elementId, content = "") {
  const element = document.getElementById(elementId);
  if (element && content) {
    element.innerHTML = content;
  }
}

// 页面动画效果
function initPageAnimations() {
  // 为卡片添加渐入动画
  const cards = document.querySelectorAll(
    ".card, .feature-card, .stat-card, .nav-item"
  );
  cards.forEach((card, index) => {
    card.style.opacity = "0";
    card.style.transform = "translateY(30px)";

    setTimeout(() => {
      card.style.transition = "opacity 0.6s ease, transform 0.6s ease";
      card.style.opacity = "1";
      card.style.transform = "translateY(0)";
    }, 100 * index);
  });

  // 数字动画效果
  animateNumbers();
}

// 鼠标跟踪效果
function initMouseTracking() {
  const featureCards = document.querySelectorAll(".feature-card");

  featureCards.forEach((card) => {
    card.addEventListener("mousemove", (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const angleX = (y - centerY) / 10;
      const angleY = (centerX - x) / 10;

      card.style.transform = `perspective(1000px) rotateX(${angleX}deg) rotateY(${angleY}deg) translateZ(10px)`;

      // 更新CSS变量用于光效
      card.style.setProperty("--mouse-x", `${(x / rect.width) * 100}%`);
      card.style.setProperty("--mouse-y", `${(y / rect.height) * 100}%`);
    });

    card.addEventListener("mouseleave", () => {
      card.style.transform =
        "perspective(1000px) rotateX(0) rotateY(0) translateZ(0)";
    });
  });
}

// 滚动动画
function initScrollAnimations() {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("fade-in");
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
      }
    });
  }, observerOptions);

  // 观察需要动画的元素
  const animatedElements = document.querySelectorAll(
    ".feature-card, .stat-card, .nav-item, .hero-description-card"
  );
  animatedElements.forEach((el) => {
    el.style.opacity = "0";
    el.style.transform = "translateY(30px)";
    el.style.transition = "opacity 0.6s ease, transform 0.6s ease";
    observer.observe(el);
  });
}

// 数字动画效果
function animateNumbers() {
  const statNumbers = document.querySelectorAll(".stat-number");

  statNumbers.forEach((stat) => {
    const finalText = stat.textContent;
    const number = parseFloat(finalText.replace(/[^\d.]/g, ""));
    const suffix = finalText.replace(/[\d.]/g, "");

    if (isNaN(number)) return;

    let current = 0;
    const increment = number / 50;
    const timer = setInterval(() => {
      current += increment;
      if (current >= number) {
        current = number;
        clearInterval(timer);
      }

      if (suffix === "+") {
        stat.textContent = Math.floor(current).toLocaleString() + "+";
      } else {
        stat.textContent = Math.floor(current).toLocaleString();
      }
    }, 30);
  });
}

// 平滑滚动
function smoothScrollTo(targetId) {
  const target = document.getElementById(targetId);
  if (target) {
    target.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }
}

// 添加涟漪效果
function addRippleEffect() {
  const buttons = document.querySelectorAll(".btn");

  buttons.forEach((button) => {
    button.addEventListener("click", function (e) {
      const ripple = document.createElement("span");
      const rect = this.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const x = e.clientX - rect.left - size / 2;
      const y = e.clientY - rect.top - size / 2;

      ripple.style.width = ripple.style.height = size + "px";
      ripple.style.left = x + "px";
      ripple.style.top = y + "px";
      ripple.classList.add("ripple");

      this.appendChild(ripple);

      setTimeout(() => {
        ripple.remove();
      }, 600);
    });
  });
}

// 初始化涟漪效果
document.addEventListener("DOMContentLoaded", addRippleEffect);
