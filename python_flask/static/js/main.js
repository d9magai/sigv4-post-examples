$(function() {
  $('#inputFile').change(function(e) {
    var file = e.target.files[0];
    console.log(file.name);
    var data = {
      name: file.name,
      size: file.size,
      content_type: file.type
    };
    $.ajax({
      url: '/signing',
      type: 'POST',
      dataType: 'json',
      data: JSON.stringify(data),
      contentType: 'application/json;charset=UTF-8',
    }).done(function(data) {
      var name, formData = new FormData();
      for (name in data.form)
        if (data.form.hasOwnProperty(name)) {
          formData.append(name, data.form[name]);
          console.log(name + ":" + data.form[name]);
        }
      formData.append('file', file);
      var xhr = new XMLHttpRequest();
      xhr.onreadystatechange = function() {
        switch (xhr.readyState) {
        case 0:
          console.log('uninitialized!');
          break;
        case 1:
          console.log('loading...');
          break;
        case 2:
          console.log('loaded.');
          break;
        case 3:
          console.log('interactive... ' + xhr.responseText.length + ' bytes.');
          break;
        case 4:
          console.log(xhr.responseText);
          if (xhr.status == 200 || xhr.status == 304) {
            var data = xhr.responseText;
            console.log('COMPLETE! :' + data);
          } else {
            console.log('Failed. HttpStatus: ' + xhr.statusText);
          }
          break;
        }
      };
      xhr.onerror = function(e) {
        console.error(xhr.statusText);
      };
      xhr.open('POST', data.url, true)
      xhr.send(formData);
    })
    $(this).val('');
  });
});
