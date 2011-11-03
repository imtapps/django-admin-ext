var AdminAjax = function($){
    return function(url, form_id, change_field_id){
        var self = this;
        self.url = url;
        self.form_id = form_id;
        self.change_field_id = change_field_id;

        $(document).ready(function(){
            self.setEvents(self.change_field_id);
        });

        self.setEvents = function(fields){
            $(fields).each(function(){
                $('#' + this).change(function(){
                    self.getForm();
                });
            });
        };

        self.getForm = function() {
            if (!self.url){
                var err_msg = "Make Sure AdminAjax is instantiated properly!";
                alert(err_msg); throw(err_msg);
            }
            $.ajax({
                url:self.url,
                data:$("#" + self.form_id).serialize(),
                cache:false,
                success: function(reply) {
                    //will potentially remove inline forms
                    $('.module').remove();
                    $('#ajax_content').html(reply);
                },
                error: function(){
                    alert("Check server logs... ajax error!");
                }
            });
        };

        return self;
    };
}(django.jQuery);
