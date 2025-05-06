class HelloWorld < Formula
  desc "Simple program that outputs 'Hello, World!'"
  homepage "https://app.lizardbyte.dev"
  url "https://github.com/LizardByte/homebrew-release-action.git"
  version "0.0.1"

  def install
    # create hello world sh file with echo command
    (buildpath/"hello-world").write <<~EOS
      #!/bin/sh
      echo "Hello, World!"
    EOS

    # install the hello-world file to the bin directory
    bin.install "hello-world"

    puts "buildpath: #{buildpath}"
  end

  test do
    system "#{bin}/hello-world"

    puts "testpath: #{testpath}"

    # test the env
    if ENV["HOMEBREW_BUILDPATH"]
      cd File.join(ENV["HOMEBREW_BUILDPATH"]) do
        # create a dummy file
        File.write("dummy.txt", "Hello, World!")
        assert_path_exists "dummy.txt"
      end
      assert_path_exists File.join(ENV["HOMEBREW_BUILDPATH"], "dummy.txt")
    end
  end
end
# Created from LizardByte/homebrew-release-action@1d5e244413bc3eb3182f607c9e9b085d1a01f65a
