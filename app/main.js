/**
 * This is not good practice bu
 * as the script (and app) is small, we put some nodes with a global scope
 * because it's easy to iterate and test.
 * 
 */
var cover = document.getElementById("cover");
// Get the first image available in container
var viewer;
if (cover) {
    viewer = cover.getElementsByTagName("img")[0]
}

var photoFileForm = document.getElementById("infos-from-image");
var photoButton = document.getElementById("photo-button");
console.log(photoButton.clientWidth)

var errorMessageNode = document.getElementById("error-message");
var labelsNode = document.getElementById("label-detected");
var presentationNode = document.getElementById("presentation");

const PUBLIC_FRIENDLY_MESSAGE = "Something went wrong. model is currently unavailable due to a large number of request."

const names = {
    'patepresseecuite': 'fromage à pâte pressée cuite',
    'patemolleacroutelavee': "fromage à pâte molle à croute lavée",
    'patemollecroutenaturelle': "fromage de chèvre",
    'patepresseenoncuite': "fromage à pâte pressée non cuite",
    "patepersillee": "fromage à pâte persillée"
}

function clearNode(node) {
    node.innerHTML = ""
}

function clearNodeID(nodeId) {
    let target = document.getElementById(nodeId)
    clearNode(target);
}

function displayResult(imagePredictionBoxes, scaleW = 1, scaleH = 1) {

    clearNode(errorMessageNode)
    clearNode(labelsNode)

    cover.classList.remove("hidden");
    labelsNode.classList.remove("hidden");
    presentationNode.classList.add("hidden")

    const label = document.createElement("p")
    const probaValue = document.createElement("p")
    const adviceText = document.createElement("p")


    probaValue.classList.add("big-value")
    label.classList.add("big-label")
    adviceText.classList.add("mini-advice")

    /**
     * Procedure for drawing bounding box
     */


    // Remove all previous bounding box
    let bb = document.getElementsByClassName('bounding-box');

    while (bb[0]) {
        bb[0].parentNode.removeChild(bb[0]);
    }


    // Always display server side advice
    if ("advice" in imagePredictionBoxes) {
        let advices = imagePredictionBoxes.advice
        adviceText.innerHTML = advices
    }

    console.log(adviceText)

    const probableCheeze = imagePredictionBoxes.predictions
    const nbCheeze = probableCheeze.length
    let cheeseList = []
    // Lets draw bounding box and label only if cheese
    if (nbCheeze == 1) {



        // While having sorted the cheese, we displya label inner text and proba
        // of the last one only, aka the most frequent

        for (let cheese of probableCheeze) {
            const square = document.createElement("div")

            label.innerText = `Du Fromage`


            if ("label" in cheese) {
                if (cheese.label in names) {
                    label.innerText = `${names[cheese.label]} `
                    cheeseList.push(`( ${(100 * cheese.probability).toPrecision(4)} %  )`)
                }
            }

            if ("probability" in cheese) {
                if (cheese.probability > 0.8 && cheese.probability <= 1) {
                    probaValue.innerText = "I'm quite sure that this is a "
                }

                if (cheese.probability > 0.6 && cheese.probability <= 0.8) {
                    probaValue.innerText = "Huum, it probably is a"
                }

                if (cheese.probability > 0.4 && cheese.probability <= 0.6) {
                    probaValue.innerText = "I am not quite sure but maybe it is a "
                }
            }


            // Draw a bounding box for each
            const [yTopRelative, xLeftRelative, yBottomRelative, xRightRelative] = cheese.detection_box

            const xLeftAbsolute = xLeftRelative * viewer.clientWidth
            const yTopAbsolute = yTopRelative * viewer.clientHeight
            const xRightAbsolute = xRightRelative * viewer.clientWidth
            const yBottomAbsolute = yBottomRelative * viewer.clientHeight

            square.classList.add('bounding-box')

            if ("label" in cheese) {
                square.classList.add(cheese.label)
            }

            if ("probability" in cheese) {
                if (cheese.probability > 0.8 && cheese.probability <= 1) {
                    square.classList.add("sure");
                }
                if (cheese.probability > 0.6 && cheese.probability <= 0.8) {
                    square.classList.add("quite-sure");
                }
                if (cheese.probability > 0.4 && cheese.probability <= 0.6) {
                    square.classList.add("not-quite-sure");
                }
                if (cheese.probability > 0 && cheese.probability <= 0.4) {
                    square.classList.add("not-sure");
                }
            }


            const { x, y } = viewer.getBoundingClientRect();
            square.style.height = `${yBottomAbsolute - yTopAbsolute}px`
            square.style.width = `${xRightAbsolute - xLeftAbsolute}px`
            square.style.position = "absolute"
            square.style.top = `${y + yTopAbsolute}px`
            square.style.left = `${x + xLeftAbsolute}px`

            viewer.parentNode.insertBefore(square, viewer.nextSibling)
        }

        console.log(cheeseList)
        console.log(cheeseList.slice(-1))
        labelsNode.append(probaValue)
        labelsNode.append(label)
        adviceText.innerText = `${adviceText.innerText}.\n${(cheeseList.slice(-1).join(","))}`


    }

    if (nbCheeze > 1) {



  
        const cheesesLabels = new Set([...probableCheeze.map(c => c.label)])
        console.log(cheesesLabels)
        const Counter ={};
        for (let currentCheese of  cheesesLabels) {
            console.log(currentCheese)
            Counter[currentCheese] = probableCheeze.filter(cheese => cheese.label === currentCheese).length
        }
        console.log(Counter)

        const sentences = Object.entries(Counter).map( ([label, count]) => `${count} ${label in names ? names[label] : "unknown"}`)
        
        probaValue.innerText = `There are ${nbCheeze} cheeses on this image ( ${sentences.join(', ')} )`

        for (let cheese of probableCheeze) {
            const square = document.createElement("div")

            if ("label" in cheese) {
                if (cheese.label in names) {

                    cheeseList.push(`( ${(100 * cheese.probability).toPrecision(4)} %  )`)
                }
            }


            // Draw a bounding box for each
            const [yTopRelative, xLeftRelative, yBottomRelative, xRightRelative] = cheese.detection_box

            const xLeftAbsolute = xLeftRelative * viewer.clientWidth
            const yTopAbsolute = yTopRelative * viewer.clientHeight
            const xRightAbsolute = xRightRelative * viewer.clientWidth
            const yBottomAbsolute = yBottomRelative * viewer.clientHeight

            square.classList.add('bounding-box')

            if ("label" in cheese) {
                square.classList.add(cheese.label)
            }

            if ("probability" in cheese) {
                if (cheese.probability > 0.8 && cheese.probability <= 1) {
                    square.classList.add("sure");
                }
                if (cheese.probability > 0.6 && cheese.probability <= 0.8) {
                    square.classList.add("quite-sure");
                }
                if (cheese.probability > 0.4 && cheese.probability <= 0.6) {
                    square.classList.add("not-quite-sure");
                }
                if (cheese.probability > 0 && cheese.probability <= 0.4) {
                    square.classList.add("not-sure");
                }
            }


            const { x, y } = viewer.getBoundingClientRect();
            square.style.height = `${yBottomAbsolute - yTopAbsolute}px`
            square.style.width = `${xRightAbsolute - xLeftAbsolute}px`
            square.style.position = "absolute"
            square.style.top = `${y + yTopAbsolute}px`
            square.style.left = `${x + xLeftAbsolute}px`

            viewer.parentNode.insertBefore(square, viewer.nextSibling)
        }

        console.log(cheeseList)
        console.log(cheeseList.slice(-1))
        labelsNode.append(probaValue)
        adviceText.innerText = `${adviceText.innerText}.\n${(cheeseList.slice(-1).join(","))}`


    }
    labelsNode.append(adviceText)
}


function displayError(msg) {
    errorMessageNode.classList.remove("hidden")
    errorMessageNode.innerHTML = msg

}


function displayImage(formIdSrc) {

    photoFileForm.addEventListener("change", async function (event) {
        event.preventDefault();

        errorMessageNode.classList.add("hidden")
        cover.classList.remove("hidden");
        labelsNode.classList.remove("hidden");

        presentationNode.classList.add("hidden")

        // We create an image and when it's loaded, 
        // we graph its dimension then call the API
        const img = new Image();
        // Image is in ram
        img.onload = async function () {
            try {
                const FD = new FormData(photoFileForm);

                const res = await fetch(photoFileForm.action, {
                    method: 'POST', // or 'PUT'
                    body: FD
                })

                if (res.ok) {
                    const pred = await res.json()
                    // Draw Square

                    displayResult(pred)

                } else {
                    throw new Error(PUBLIC_FRIENDLY_MESSAGE)
                }

            } catch (error) {
                console.error(error)
                displayError(PUBLIC_FRIENDLY_MESSAGE)
            }
        }

        viewer.src = URL.createObjectURL(event.target.files[0]);
        img.src = URL.createObjectURL(event.target.files[0]);

        // Because flex box direction may change
        let box_w, box_h
        if (cover.clientHeight !== 0) {
            box_h = cover.clientHeight
            box_w = photoButton.clientWidth
        }
        if (cover.clientWidth !== 0) {
            box_w = cover.clientWidth
            box_h = photoButton.clientHeight
        }

        // Use the phot h button size as ref
        // as the cover fit with the image
        console.log(`${box_w},${box_h}`)


        viewer.onload = function () {

            const ratio = this.width / this.height;
            console.log('------------------------------')


            if (this.width > box_w) {
                console.log('Case 1')
                this.width = box_w;
                this.height = this.width / ratio;
            }


            if (this.height > box_h) {
                console.log('Case 2')
                this.height = box_h
                this.width = ratio * this.height
            }

            console.log(`Image is ${this.height}x${this.width}`)
            console.log(`Cover is ${this.offsetHeight}x${this.offsetWidth}`)


            URL.revokeObjectURL(viewer.src) // free memory

        }
    });
}

// When everythong is ok
window.addEventListener("load", function () {

    displayImage()

});