const animation = () => {
    const info = Array.from(document.querySelectorAll('.input-group'))
    const button = Array.from(document.querySelectorAll(".toggle-btn"))
    const btn = document.querySelector('#btn')
    button[0].addEventListener('click', ()=>{
        if(btn.classList[0] != 'left'){
        btn.classList.toggle('left')
        btn.classList.remove('right')
        info[0].classList.toggle('loginin')
        info[0].classList.remove('loginreg')
        info[1].classList.toggle('registerin')
        info[1].classList.remove('registerreg')
    }})
    button[1].addEventListener('click', ()=>{
        if(btn.classList[0] != 'right'){
        btn.classList.toggle('right')
        btn.classList.remove('left')
        info[0].classList.toggle('loginreg')
        info[0].classList.remove('loginin')
        info[1].classList.toggle('registerreg')
        info[1].classList.remove('registerin')
      }})
}
animation()