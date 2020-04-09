---
layout: post
title: Dockerfile Composition
tags: [docker, hierarchy, software architecture]
---

Dockerfiles are great when you have one image that you need to generate. But what happens if you need to generate several images that are substantially similar, but differ in a few aspects? This post will talk about how to compose your Dockerfiles so that you can reduce complexity and duplication, but still have flexibility to generate multiple final images from a single project.

![](/public/images/2020/03/24/header-image.png)

<!--endexcerpt-->

# Use Cases

The primary use case that I have encountered is when you have a single project that operates on multiple products. Suppose that you have other constraints on the image that is delivered to the run location. These constraints could be to minimize the image size, reduce the amount of bundled IP, or perhaps the architecture that it runs on. In all of these cases you will need to be selective about what makes it into the final image.

As a simple example, you could have a web server that displays pictures that are included in the Docker image. Using the composition techniques below, you can have Docker include pictures of cats, dogs, or kinkajous. For this example, each variant would simply be a different `COPY`.

The three composition methods presented here are:
* Classic multi-image method
* Fan-out method
* Fan-in method


# Classic Multi-Image Method

This is the mechanism that Docker has supported from the beginning. It's useful when you want to have a strict separation between the base image and it's variations.

![multi-image method](/public/images/2020/03/24/multi-image-method.png)

We start with a base image that installs the common features:

```dockerfile
FROM ubuntu:18.04 as base
RUN echo "base" >> /history.txt
CMD cat /history.txt
```

Then we need to build the image:

```bash
docker build --file=multi-image.base.dockerfile --tag=multi-image/base ./
```

From there, we can develop as many variations as we like. For example, using variant0:

```dockerfile
FROM multi-image/base
RUN echo "variant0" >> /history.txt
```

Build the variation:

```bash
docker build --file=multi-image.variant0.dockerfile --tag=multi-image/variant0 ./
```

Run the variation:

```bash
$ docker run multi-image/variant0
base
variant0
```

Essentially, the `variant0` image has "inherited" everything from the `base` image. If we examine our local image list, we can see that there's both a `multi-image/base` image and a `multi-image/variant0` image.

One potential issue with this method is that Docker can't detect if the base image is updated, so doesn't know if it needs to be re-pulled or re-built. Your build scripts will need to handle this case. On the other hand, if you have a very strict versioning policy this could be helpful: variant images can specify an exact variant to use.


# Fan-Out Method

In the fan methods, we make use of Docker's multi-stage build feature. Multi-stage builds are a handy way to have multiple `FROM` statements in the same Dockerfile. In this case, it's almost like taking the multi-image Dockerfiles and putting them into a single file. We then use some extra flags to the `docker build` command and we're done.

![fan-out method](/public/images/2020/03/24/fan-out-method.png)

We start with the Dockerfile:

```dockerfile
FROM ubuntu:18.04 as base
RUN echo "base" >> /history.txt
CMD cat /history.txt


FROM base as variant0
RUN echo "variant0" >> /history.txt

FROM base as variant1
RUN echo "variant1" >> /history.txt

FROM base as variant2
RUN echo "variant2" >> /history.txt
```

Build the fan-out images with a `--target` argument to `docker build`:

```bash
docker build --file=fan-out.dockerfile --target=variant0 --tag=fan-out/variant0 ./
```

And run like normal:

```bash
$ docker run fan-out/variant0
base
variant0
```

One advantage of this method over the multi-image method is that everything is in a single file. If you're variations are pretty small then this could be handy.

A second advantage is that Docker is able to automatically detect changes is the `base` layer, and every time you build a `variant` layer those changes will be propagated automatically.


# Fan-In Method

In the fan-in method we start with a base for each of the variants, then select a variant to build the final image on top of.

![fan-in method](/public/images/2020/03/24/fan-in-method.png)

The fan-in Dockerfile:

```dockerfile
ARG variant

FROM ubuntu:18.04 as variant0
RUN echo "variant0" >> /history.txt

FROM ubuntu:18.04 as variant1
RUN echo "variant1" >> /history.txt

FROM ubuntu:18.04 as variant2
RUN echo "variant2" >> /history.txt

FROM $variant as join
# pass, do nothing

FROM ubuntu:18.04 as final
COPY --from=join /history.txt /
RUN echo "final" >> /history.txt
CMD cat /history.txt
```

We need to have a `join` stage in order to copy the files that we're interested in. You might think that we could do something like `COPY --from=$variant /history.txt /` in order to cherry pick just those files. Unfortunately, that won't work since Docker doesn't support variables in `--from` ([2+ year old bug report](https://github.com/moby/moby/issues/34482)). So instead, we create a stage with a known and constant name, and copy from that.

To build, we always build the same target (`final`), but we tag it with the variant. To get the Dockerfile to build the correct variant, we pass in a `--build-arg`.

```bash
docker build --file=fan-in.dockerfile --target=final --build-arg="variant=variant1" --tag=fan-in/variant1 ./
```

And again, run like normal:

```bash
$ docker run fan-in/variant1
variant1
final
```

The fan-in method is very handy when you have a number of projects that have different files, but those files are built in the same way. In that case you can load the files in a variant, then run the build steps in the `final` stage.
