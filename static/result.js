const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
let interval = null;
const swiftUpElements = document.querySelectorAll('.swift-up-text');

document.querySelector('.title').onmouseover = (event) => {
  let iteration = 0;

  clearInterval(interval);

  interval = setInterval(() => {
    event.target.innerText = event.target.innerText
      .split('')
      .map((letter, index) => {
        if (index < iteration) {
          return event.target.dataset.value[index];
        }
        return letters[Math.floor(Math.random() * 26)];
      })
      .join('');
    if (iteration >= event.target.dataset.value.length) {
      clearInterval(interval);
    }
    iteration += 1 / 3;
  }, 50);
};



swiftUpElements.forEach(elem => {

	const words = elem.textContent.split(' ');
	elem.innerHTML = '';

	words.forEach((el, index) => {
		words[index] = `<span><i>${words[index]}</i></span>`;
	});

	elem.innerHTML = words.join(' ');

	const children = document.querySelectorAll('span > i');
	children.forEach((node, index) => {
		node.style.animationDelay = `${index * .2}s`;
	});

});