CC = gcc
CFLAGS = -fPIC -O2 -Wall -Wextra
LDFLAGS = -shared -ldl -lm

TARGET = LinuxSO.so
SOURCES = LinuxSO.c
OBJECTS = $(SOURCES:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(LDFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c $<

clean:
	rm -f $(OBJECTS) $(TARGET)

.PHONY: all clean
