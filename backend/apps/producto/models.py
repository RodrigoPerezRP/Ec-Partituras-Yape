from django.db import models
from django.utils.text import slugify

class CategoriaProducto(models.Model):

    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

class Producto(models.Model):

    DIFICULTAD_CHOICES = (
        ('facil', 'Fácil'),
        ('intermedio', 'Intermedio'),
        ('dificil', 'Difícil'),
    )

    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    dificultad = models.CharField(
        max_length=20,
        choices=DIFICULTAD_CHOICES
    )
    arreglista = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    portada = models.ImageField(upload_to='portadas/')
    datecreated = models.DateTimeField(auto_now_add=True)
    tieneFinale = models.BooleanField(default=False)
    tieneAudio = models.BooleanField(default=False)
    tieneDestacado = models.BooleanField(default=False)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='files/')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre
    
