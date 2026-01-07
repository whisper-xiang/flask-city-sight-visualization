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
});

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
