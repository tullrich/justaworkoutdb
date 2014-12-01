$(function() {
    // Datepicker
    $("input[type='text'].input-datepicker").pickadate({
        formatSubmit: 'yyyy-mm-dd',
        hiddenName: true,
        editable: true
    });

    // Remove workout session ajax.
    $(".erase-workout").click(function( e ){
        var ele = $(this);
        var workoutId = ele.data('workout-id');
        if(!workoutId || ele.data("jqxhr"))
            return false;
        ele.html("<i class=\"fa fa-spin fa-spinner\"></i");
        ele.data("jqxhr", $.post( "workouts/remove", { id:workoutId })
            .fail( function( data ){
                ele.html("<i class=\"fa fa-close\"></i");
                ele.removeData();
            }).done( function ( data ){
                ele.parents(".workout").remove();
        }));
        return false;
    });

    var logItemTemplate = Handlebars.compile($("#entry-template").html());

    var addLogItem = function( exerciseId, exerciseName ){
        $('#logged_exercises').append(logItemTemplate({itemId:$('#logged_exercises li').length, exerciseId:exerciseId, exerciseName:exerciseName}));
    };

    // Add log item to dynamic form.
    $("#add-log-item").change(function( e ){
        var newVal = $(this).val();
        if(newVal == null )
            return;

        addLogItem(newVal, $('#add-log-item option:selected').text());
        $(this).val(-1);
        return false;
    });

    // Remove log item from dynamic form.
    $("form.add-exercise").on("click", ".erase-logged_item", function( e ){
        $(this).parents("li").remove();
        return false;
    });
});