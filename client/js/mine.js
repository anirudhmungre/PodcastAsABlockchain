let i = 0;

const mine = () => {
    i = i + 1;
    postMessage(i);
    setTimeout("mine()", 1000);
}

mine();