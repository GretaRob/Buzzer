

function edit(id) {
  var edit_box = document.querySelector(`#edit-box-${id}`);
  var edit_btn = document.querySelector(`#edit-btn-${id}`);
  edit_box.style.display = 'block';
  edit_btn.style.display = 'block';

  //prefill composition field
  
    var text_area = document.getElementById(`edit-box-${id}`);
    var post_content = document.getElementById(`post-${id}`).textContent;
    text_area.innerHTML = post_content.trim();
 

  edit_btn.addEventListener('click', () => {
      fetch(`/edit/${id}`, {
          method: 'PUT',
          body: JSON.stringify({
              post: edit_box.value
          })
        });
      
        edit_box.style.display = 'none';
        edit_btn.style.display = 'none';

        document.querySelector(`#post-${id}`).innerHTML = edit_box.value;
  });

 
}


async function like(id) {
    var like_btn = document.querySelector(`#like-btn-${id}`);
    var like_ct = document.querySelector(`#like-count-${id}`);
  
    like_btn.disabled = true;
  
        if (like_btn.style.color == 'grey') {
            await fetch(`/like/${id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    like: true
                })
              })
  
            like_btn.style.color = 'lightseagreen';
              
            await fetch(`/like/${id}`)
            .then(response => response.json())
            .then(post => {
                like_ct.innerHTML = post.likes;
            });
        }
        else {
            await fetch('/like/' + id, {
                method: 'PUT',
                body: JSON.stringify({
                    like: false
                })
              });
              
            like_btn.style.color = 'grey';
  
            await fetch(`/like/${id}`)
            .then(response => response.json())
            .then(post => {
                like_ct.innerHTML = post.likes;
            });
        }
        

  
  }

function deletepost(id) {
    fetch(`/deletepost/${id}`, {
        method: 'DELETE'
    })
    .then(() => {
        window.location.reload();
    }
     )
    .catch(err => {
       console.error(err)
     });
}