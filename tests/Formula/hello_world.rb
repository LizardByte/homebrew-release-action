class HelloWorld < Formula
  desc "Simple program that outputs 'Hello, World!'"
  homepage "https://app.lizardbyte.dev"
  url "https://github.com/LizardByte/homebrew-release-action.git"
  version "0.0.1"

  INSTALL_FILENAME = "hello-world".freeze
  HELLO_WORLD_BASH = <<~EOS.freeze
    #!/bin/sh
    echo "Hello, World!"
  EOS

  def install
    # create hello world sh file with echo command
    filename = buildpath/INSTALL_FILENAME
    File.write(filename, HELLO_WORLD_BASH)

    # install the hello-world file to the bin directory
    bin.install filename

    puts "buildpath: #{buildpath}"
  end

  test do
    assert_equal "Hello, World!\n", shell_output("#{bin}/hello-world")

    puts "testpath: #{testpath}"

    # test the env
    if ENV["HOMEBREW_BUILDPATH"]
      dummy_filename = "dummy.txt"
      cd File.join(ENV["HOMEBREW_BUILDPATH"]) do
        # create a dummy file
        File.write(dummy_filename, "Hello, World!")
        assert_path_exists dummy_filename
      end
      assert_path_exists File.join(ENV["HOMEBREW_BUILDPATH"], dummy_filename)

      # test if we can read the file created during the install
      assert_path_exists File.join(ENV["HOMEBREW_BUILDPATH"], INSTALL_FILENAME)
      assert_equal File.read(File.join(ENV["HOMEBREW_BUILDPATH"], INSTALL_FILENAME), HELLO_WORLD_BASH)
    end
  end
end
