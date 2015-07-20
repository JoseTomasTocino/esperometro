var gulp = require('gulp');
var sass = require('gulp-sass');
var livereload = require('gulp-livereload');

var paths = {
    templates : ['templates/**/*'],
    sass_styles : ['static/sass/**/*'],
    styles : ['static/**/*']
};

gulp.task('sass', function() {
    gulp.src(paths.sass_styles)
        .pipe(sass().on('error', sass.logError))
        .pipe(gulp.dest('./static/css'))
        .pipe(livereload())
});

gulp.task('templates', function() {
    gulp.src(paths.templates)
        .pipe(livereload());
});

gulp.task('watch', function(){
    livereload.listen();
    gulp.watch(paths.styles, ['sass']);
    gulp.watch(paths.templates, ['templates']);
})