/*
 *   This content is licensed according to the W3C Software License at
 *   https://www.w3.org/Consortium/Legal/2015/copyright-software-and-document
 *
 *   File:  switch-checkbox.js
 *
 *   Desc:  Switch widget using input[type=checkbox] that implements ARIA Authoring Practices
 */

'use strict';

// Objeto global para guardar el estado de los switches
window.switchStates = {};

class CheckboxSwitch {
  constructor(domNode) {
    this.switchNode = domNode;
    this.id = this.switchNode.id; // usamos el ID para identificar el switch

    // Inicializamos el estado en el objeto global
    window.switchStates[this.id] = this.switchNode.checked ? 'on' : 'off';

    // Eventos
    this.switchNode.addEventListener('focus', (event) => this.onFocus(event));
    this.switchNode.addEventListener('blur', (event) => this.onBlur(event));
    this.switchNode.addEventListener('change', (event) => this.onChange(event));
  }

  onFocus(event) {
    event.currentTarget.parentNode.classList.add('focus');
  }

  onBlur(event) {
    event.currentTarget.parentNode.classList.remove('focus');
  }

  onChange(event) {
    const isChecked = event.currentTarget.checked;

    // Actualizamos el objeto global
    window.switchStates[this.id] = isChecked ? 'on' : 'off';

    // Log
    console.log(`${this.id} is now ${window.switchStates[this.id]}`);
  }
}

// Inicializar switches
window.addEventListener('load', function () {
  Array.from(
    document.querySelectorAll('input[type=checkbox][role^=switch]')
  ).forEach((element) => new CheckboxSwitch(element));
});